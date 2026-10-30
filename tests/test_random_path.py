"""Random price path inside a forming candle, and the internship features off by default.

Fan (30 Oct 2026): "Yes, you can add the random path. But this method should also be
activated or disabled in the configuration. Every implemented function should be
disabled and let user select what they want."
"""
import io
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import pytest

from trade.defaults import defaults as dlt
from trade.utils import candle_steps as cs
from trade.utils.graph.candlestick_charts import chart_config
from trade.utils.session import build_session_zip, extract_session_zip
import trade.callbacks.dashboard.request as request
import trade.callbacks.dashboard.leaderboard as board
import trade.callbacks.dashboard.graph as graph
import trade.callbacks.settings.advanced as advanced
from conftest import SHORT_DAYS

TRADE = Path(__file__).resolve().parents[1] / "trade"


# ── The random path ───────────────────────────────────────────────────────

@pytest.mark.parametrize("n_steps", [2, 4, 12])
def test_random_path_starts_at_open_ends_at_close_and_touches_high_and_low(market_df, real_candle, n_steps):
    for ts in market_df.index[:SHORT_DAYS]:
        o, h, l, c = real_candle("AAA", ts)
        path = cs._random_path(o, h, l, c, n_steps, cs._seed("AAA", ts))
        assert len(path) == n_steps * cs.TICKS_PER_STEP + 1
        assert path[0] == o and path[-1] == c
        assert path.max() == h and path.min() == l          # inside the real candle, reaches both ends


@pytest.mark.parametrize("n_steps", [2, 4, 12])
def test_random_path_ends_on_the_real_candle_and_only_grows(market_df, real_candle, n_steps):
    for ts in market_df.index[:SHORT_DAYS]:
        o, h, l, c = real_candle("AAA", ts)
        prev_high, prev_low = -math.inf, math.inf
        for step in range(1, n_steps + 1):
            so, sh, sl, sc = cs.partial_candle("AAA", ts, step, n_steps, "random")
            assert so == o and l <= sl <= sc <= sh <= h
            assert sh >= prev_high and sl <= prev_low
            prev_high, prev_low = sh, sl
        assert cs.partial_candle("AAA", ts, n_steps, n_steps, "random") == real_candle("AAA", ts)


def test_random_path_is_the_same_for_every_participant(market_df):
    ts = market_df.index[110]
    first = [cs.partial_candle("AAA", ts, k, 4, "random") for k in range(1, 5)]
    cs._steps.cache_clear()
    assert [cs.partial_candle("AAA", ts, k, 4, "random") for k in range(1, 5)] == first


def test_random_path_differs_from_the_simple_one(market_df, real_candle):
    different = 0
    for ts in market_df.index[:SHORT_DAYS]:
        o, h, l, c = real_candle("AAA", ts)
        seed = cs._seed("AAA", ts)
        if not np.array_equal(cs._random_path(o, h, l, c, 4, seed), cs._path(o, h, l, c, 4, seed)):
            different += 1
    assert different == SHORT_DAYS


def test_random_path_can_reach_the_high_or_the_low_first(market_df, real_candle):
    """Simple: an up candle always goes to its Low first, a down candle to its High.
    Random: either one can come first, so the shape is not always the same."""
    simple_order, random_order = set(), set()
    for ts in market_df.index:
        candle = real_candle("AAA", ts)
        if candle is None or any(math.isnan(v) for v in candle):
            continue
        o, h, l, c = candle
        if h == l or c < o:
            continue                                         # up candles only
        seed = cs._seed("AAA", ts)
        for path, seen in ((cs._path(o, h, l, c, 4, seed), simple_order),
                           (cs._random_path(o, h, l, c, 4, seed), random_order)):
            seen.add("low first" if np.argmin(path) < np.argmax(path) else "high first")
    assert simple_order == {"low first"}
    assert random_order == {"low first", "high first"}


def test_simple_is_the_default_and_unchanged(market_df):
    ts = market_df.index[110]
    for k in range(1, 5):
        assert cs.partial_candle("AAA", ts, k, 4) == cs.partial_candle("AAA", ts, k, 4, "simple")
        assert cs.partial_candle("AAA", ts, k, 4, None) == cs.partial_candle("AAA", ts, k, 4, "simple")


def test_random_prices_stay_in_the_step_range(market_df, real_candle):
    for ts in market_df.index[:SHORT_DAYS]:
        o, h, l, c = real_candle("AAA", ts)
        for step in range(1, 5):
            lo, hi = cs.step_price_range("AAA", ts, step, 4, "random")
            assert l <= lo <= hi <= h
            assert lo <= cs.current_price("AAA", ts, step, 4, "random") <= hi


def test_flat_candle_does_not_move():
    assert (cs._random_path(10.0, 10.0, 10.0, 10.0, 4, 1) == 10.0).all()


# ── The setting reaches the chart, the orders and the leaderboard ─────────

def test_market_price_button_uses_the_chosen_path(market_df):
    ts = market_df.index[110]
    price = request.fill_market_price(1, "AAA", ts, 2, 4, "random")
    assert price == round(cs.current_price("AAA", ts, 2, 4, "random"), 2)


def test_orders_are_checked_on_the_chosen_path(market_df, monkeypatch):
    seen = []

    def spy(company, timestamp, step, n_steps, path="simple"):
        seen.append(path)
        return cs.step_price_range(company, timestamp, step, n_steps, path)
    monkeypatch.setattr(request, "step_price_range", spy)
    order = {"company": "AAA", "action": "buy", "price": 1.0, "shares": 1}
    request.execute_requests([order], market_df.index[110], 2, {"AAA": 0, "BBB": 0}, 100_000,
                             {"AAA": 0, "BBB": 0}, {}, {}, 4, False, "random")
    assert seen and set(seen) == {"random"}


def test_leaderboard_uses_the_chosen_path(fake_data, monkeypatch):
    from trade.utils.market import get_market_dataframe
    seen = {}
    real = board.robots_at

    def spy(*args, price_now=None, **kwargs):
        seen["price_now"] = price_now
        return real(*args, price_now=price_now, **kwargs)
    monkeypatch.setattr(board, "robots_at", spy)
    df = get_market_dataframe()
    companies = {"AAA": {"label": "AAA", "got_charts": True}, "BBB": {"label": "BBB", "got_charts": True}}
    board.update_leaderboard(df.index[110], {}, 100_000, [], True, 100, 100_000, companies, "?lang=en", 0,
                             1, 4, "random")
    assert seen["price_now"]("AAA") == pytest.approx(cs.current_price("AAA", df.index[110], 1, 4, "random"))


def test_chart_callback_reads_the_path_setting():
    code = (TRADE / "callbacks" / "dashboard" / "graph.py").read_text(encoding="utf-8")
    assert "State('candle-path', 'data')" in code
    assert "partial_candle(company, ts, new_step, n_steps, candle_path)" in code


def test_path_setting_is_saved_and_shown():
    assert advanced.save_candle_path_setting("random") == "random"
    assert advanced.save_candle_path_setting("bad") == "simple"
    assert advanced.show_candle_path_setting("settings", None) == "simple"
    assert advanced.show_candle_path_setting("settings", "random") == "random"


# ── Autoscale / Reset axes buttons ────────────────────────────────────────

def test_chart_buttons_hidden_when_off():
    removed = chart_config(False)["modeBarButtonsToRemove"]
    assert "autoScale2d" in removed and "resetScale2d" in removed
    assert graph.show_chart_buttons(None) == chart_config(False)


def test_chart_buttons_shown_when_on():
    config = graph.show_chart_buttons(True)
    assert "autoScale2d" not in config["modeBarButtonsToRemove"]
    assert "resetScale2d" not in config["modeBarButtonsToRemove"]
    assert config["displayModeBar"] is True


def test_chart_buttons_switch_saves():
    assert advanced.save_chart_buttons_setting(True) is True
    assert advanced.show_chart_buttons_setting("settings", None) is False


# ── Off by default ────────────────────────────────────────────────────────

def test_internship_features_are_off_by_default():
    app_code = (TRADE / "app.py").read_text(encoding="utf-8")
    assert dlt.steps_per_candle == 1                     # moving candles off
    assert dlt.candle_path == "simple"
    for store in ("reminders-enabled", "leaderboard-enabled", "discrete-enabled", "chart-buttons-enabled"):
        assert f'dcc.Store(id="{store}", data=False' in app_code, store
    assert dlt.commission_fee == 0
    news_layout = (TRADE / "layouts" / "settings" / "sections" / "news.py").read_text(encoding="utf-8")
    assert 'id="reminders-enabled-input",\n                label=tl["notifications"]["reminders-label"],\n                checked=False' in news_layout


# ── Session file ──────────────────────────────────────────────────────────

def test_session_file_carries_the_new_settings(fake_data, tmp_path):
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data), candle_path="random", chart_buttons_enabled=True)
    stores = extract_session_zip(raw, str(tmp_path))
    assert stores["candle-path"] == "random"
    assert stores["chart-buttons-enabled"] is True


def test_new_session_file_defaults_are_off(fake_data, tmp_path):
    stores = extract_session_zip(build_session_zip({}, 100_000, 10, 5000, str(fake_data)), str(tmp_path))
    assert stores["candle-path"] == "simple"
    assert stores["chart-buttons-enabled"] is False
    assert stores["reminders-enabled"] is False
    assert stores["steps-per-candle"] == 1


def test_old_session_files_get_simple_path_and_no_buttons(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("session.json", json.dumps({"version": 1, "stores": {
            "companies": {}, "initial-cashflow": 100_000, "max-requests": 10, "update-time": 5000}}))
    stores = extract_session_zip(buf.getvalue(), str(tmp_path))
    assert stores["candle-path"] == "simple"
    assert stores["chart-buttons-enabled"] is False
