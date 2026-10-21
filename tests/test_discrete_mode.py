"""Discrete mode: the session is a list of trials ("10, 15") instead of a running clock.

Trial 1 shows candles 1-10 and waits; "Next trial" checks the waiting orders on the
candles in between (11..15) and shows candles 1-15. After the last trial the session
ends. An order at the market price is executed at once; others wait."""
import io
import json
import time
import zipfile
from types import SimpleNamespace

import pandas as pd
import pytest
from dash.exceptions import PreventUpdate

import trade.callbacks.dashboard.graph as graph
import trade.callbacks.dashboard.request as request
import trade.callbacks.dashboard.trials as trials_cb
import trade.callbacks.settings.advanced as advanced
from trade.utils import trials
from trade.utils.session import build_session_zip, extract_session_zip

CHECKPOINTS = [105, 110]      # the fake data has 160 candles


# ── The candle list ──────────────────────────────────────────────────────

@pytest.mark.parametrize("text, expected", [
    ("10, 15", [10, 15]),
    (" 10,15 , 150 ", [10, 15, 150]),
    ("10; 15", [10, 15]),
    ("15, 10", None),          # must go up
    ("10, 10", None),
    ("1, 10", None),           # candle 1 alone isn't a chart
    ("10, 500", None),         # past the end of the data
    ("ten", None),
    ("", None),
])
def test_candle_list_is_checked(text, expected):
    assert trials.parse_checkpoints(text, 200) == expected


def test_session_opens_on_the_first_trial():
    assert trials.history_bars([10, 15]) == 9          # rows 0..9 = candles 1..10


def test_trial_position_and_next():
    assert trials.trial_position([10, 15], 10) == (1, 2)
    assert trials.trial_position([10, 15], 15) == (2, 2)
    assert trials.next_checkpoint([10, 15], 10) == 15
    assert trials.next_checkpoint([10, 15], 15) is None


# ── The supervisor's example: day 10 = 10€, day 13 = 8€, day 15 = 15€ ─────

def example_market():
    closes = [10] * 10 + [9.5, 9, 8.2, 12, 15]
    lows = [c - 0.1 for c in closes]
    lows[12] = 8.0                                     # day 13 reaches 8€
    df = pd.DataFrame({("AAA", "Low"): lows, ("AAA", "High"): [c + 0.1 for c in closes],
                       ("AAA", "Close"): closes},
                      index=[f"2025-01-{d:02d}" for d in range(1, 16)])
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df


def test_buy_at_8_placed_on_day_10_is_filled_on_day_13():
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": 8.0, "fee": 0}
    waiting, basis, sold = [order], {}, {}
    shares, cash = trials.walk_orders(example_market(), 10, 15, waiting, {"AAA": 0}, 0, basis, sold)
    assert waiting == []                               # the order has passed
    assert shares["AAA"] == 10
    assert basis["AAA"] == pytest.approx(80)           # bought at 8€, not at a later price
    assert cash == pytest.approx(0)                    # the 80€ put aside paid for it
    assert 10 * 15 - basis["AAA"] == pytest.approx(70)  # profit seen on day 15


def test_order_never_reached_keeps_waiting():
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": 5.0, "fee": 0}
    waiting = [order]
    shares, _ = trials.walk_orders(example_market(), 10, 15, waiting, {"AAA": 0}, 50, {}, {})
    assert waiting == [order]
    assert shares["AAA"] == 0


def test_sell_waiting_for_a_higher_price_is_filled_when_reached():
    order = {"action": "sell", "shares": 10, "company": "AAA", "price": 14.0, "fee": 0}
    waiting, sold = [order], {}
    shares, cash = trials.walk_orders(example_market(), 10, 15, waiting, {"AAA": 10}, 0, {}, sold)
    assert shares["AAA"] == 0
    assert cash == pytest.approx(150)                  # day 15 closes at 15€ (more than 14€)


# ── Orders during a trial: market price at once, the others wait ──────────

def run(order, market_df, discrete, cash=100_000):
    out = request.execute_requests([dict(order)], market_df.index[109], None, {"AAA": 0, "BBB": 0}, cash,
                                   {"AAA": 0.0, "BBB": 0.0}, {}, {}, 1, discrete)
    return out[0] is not request.no_update and out[0] == []          # executed?


def test_order_at_market_price_is_executed_at_once(market_df, real_candle):
    close = real_candle("AAA", market_df.index[109])[3]
    order = {"action": "buy", "shares": 1, "company": "AAA", "price": round(close + 1, 2), "fee": 0}
    assert run(order, market_df, discrete=True)


def test_lower_price_waits_for_the_next_trial(market_df, real_candle):
    _, _, low, close = real_candle("AAA", market_df.index[109])
    order = {"action": "buy", "shares": 1, "company": "AAA", "price": round((low + close) / 2, 2), "fee": 0}
    if low >= close - 0.02:
        pytest.skip("this fake candle closed at its low")
    assert not run(order, market_df, discrete=True)
    assert run(order, market_df, discrete=False)                      # continuous mode as before


# ── The "Next trial" button ──────────────────────────────────────────────

def test_next_trial_jumps_and_fills_orders_on_the_candles_in_between(market_df, real_candle):
    lows = [real_candle("AAA", ts)[2] for ts in market_df.index[105:110]]      # candles 106..110
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": round(min(lows) + 0.01, 2), "fee": 0}
    out = trials_cb.next_trial(1, market_df.index[104], True, CHECKPOINTS, [order], {"AAA": 0, "BBB": 0},
                               100_000 - 10 * order["price"], {}, {}, "AAA", None)
    assert out[0] == market_df.index[109]               # chart now up to candle 110
    assert out[1] == []                                 # the order has passed
    assert out[2]["AAA"] == 10
    assert out[7] == 110                                # asks for the new chart


def test_after_the_last_trial_the_session_ends(market_df):
    out = trials_cb.next_trial(1, market_df.index[109], True, CHECKPOINTS, [], {}, 100_000, {}, {}, "AAA", None)
    assert out[8] is True                               # results window
    assert out[0] is trials_cb.no_update                # no jump


def test_button_says_which_trial(market_df):
    style, label = trials_cb.show_next_trial_button(market_df.index[104], True, CHECKPOINTS, "?lang=en")
    assert style == {"display": "block"}
    assert label == "Next trial ➔ (1/2)"
    _, label = trials_cb.show_next_trial_button(market_df.index[109], True, CHECKPOINTS, "?lang=en")
    assert label == "Finish ➔ (2/2)"


def test_no_button_in_normal_mode(market_df):
    style, _ = trials_cb.show_next_trial_button(market_df.index[104], False, CHECKPOINTS, "?lang=en")
    assert style == {"display": "none"}


# ── The chart: no running clock ──────────────────────────────────────────

def draw(market_df, monkeypatch, trigger, i, started):
    monkeypatch.setattr(graph, "ctx", SimpleNamespace(triggered_id=trigger))
    return graph.update_graph(1, "AAA", market_df.index[i], started, 15, 0, [], "light", True, None,
                              100_000, None, 4, 104, 2000, 10, 100_000, {}, "session-1",
                              discrete=True, checkpoints=CHECKPOINTS)


def test_timer_does_nothing_once_the_session_has_started(market_df, monkeypatch):
    with pytest.raises(PreventUpdate):
        draw(market_df, monkeypatch, "periodic-updater", 104, time.time())


def test_first_tick_starts_the_session_without_moving_and_stops_the_timer(market_df, monkeypatch):
    out = draw(market_df, monkeypatch, "periodic-updater", 104, None)
    assert out[0] == market_df.index[104]               # still on trial 1
    assert out[2] is True                               # timer switched off
    assert out[4] is not None                           # session started


def test_next_trial_draws_the_new_chart(market_df, monkeypatch):
    out = draw(market_df, monkeypatch, "trial-jump", 109, time.time())
    assert out[0] == market_df.index[109]
    assert len(out[1].data[-1].x) == 110                # candles 1..110 on the chart


# ── Settings ─────────────────────────────────────────────────────────────

VALUES = (5000, 10, 100_000, 15, "S", "4", 100)


def test_saving_discrete_mode_sets_the_start(fake_data):
    out = advanced.update_advanced_settings(1, *VALUES, "?lang=en", 0, True, "105, 110")
    assert out[6] == 104                                # history candles: session opens on candle 105
    assert out[8] is True
    assert out[9] == [105, 110]
    assert out[-1].title == "Settings updated"


@pytest.mark.parametrize("text", ["110, 105", "105, 500", "abc"])
def test_wrong_candle_list_is_refused(fake_data, text):
    out = advanced.update_advanced_settings(1, *VALUES, "?lang=en", 0, True, text)
    assert out[-1].title == "Error"
    assert out[8] is advanced.no_update


def test_normal_mode_ignores_the_candle_list(fake_data):
    out = advanced.update_advanced_settings(1, *VALUES, "?lang=en", 0, False, "nonsense")
    assert out[6] == 100
    assert out[8] is False


def test_discrete_mode_is_kept_in_session_files(fake_data, tmp_path):
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data), discrete_enabled=True, discrete_checkpoints=[10, 15])
    stores = extract_session_zip(raw, str(tmp_path))
    assert stores["discrete-enabled"] is True
    assert stores["discrete-checkpoints"] == [10, 15]


def test_old_session_files_play_with_the_clock(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("session.json", json.dumps({"version": 1, "stores": {
            "companies": {}, "initial-cashflow": 100_000, "max-requests": 10, "update-time": 5000}}))
    assert extract_session_zip(buf.getvalue(), str(tmp_path))["discrete-enabled"] is False
