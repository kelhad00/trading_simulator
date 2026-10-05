"""Order book with moving candles: orders only use prices of the current step, never the future."""
import pytest

from trade.utils import candle_steps as cs
import trade.callbacks.dashboard.request as request


@pytest.fixture
def ts(market_df):
    return market_df.index[110]


def run_orders(orders, ts, step, shares=None, cash=100_000):
    shares = shares or {"AAA": 0, "BBB": 0}
    out = request.execute_requests(list(orders), ts, step, dict(shares), cash, dict(shares), {}, {}, 4)
    waiting = orders if out[0] is request.no_update else out[0]
    return waiting, out[1], out[3]          # orders still waiting, shares, portfolio values


def test_buy_reached_during_this_step_is_filled_at_no_more_than_the_limit(ts):
    low, high = cs.step_price_range("AAA", ts, 2, 4)
    order = {"company": "AAA", "action": "buy", "price": round(low + 0.01, 4), "shares": 10}
    waiting, shares, _ = run_orders([order], ts, 2)
    assert waiting == [] and shares["AAA"] == 10


def test_buy_below_this_steps_prices_keeps_waiting(ts):
    low, _ = cs.step_price_range("AAA", ts, 2, 4)
    order = {"company": "AAA", "action": "buy", "price": round(low - 5, 4), "shares": 10}
    waiting, shares, _ = run_orders([order], ts, 2)
    assert waiting == [order] and shares["AAA"] == 0


def test_buy_is_never_filled_by_a_price_from_later_in_the_candle(market_df, real_candle):
    """At 15 min, an order at a price the candle only reaches later must wait."""
    checked = 0
    for ts in market_df.index[:110]:
        candle_low = real_candle("AAA", ts)[2]
        step1_low, _ = cs.step_price_range("AAA", ts, 1, 4)
        if step1_low - candle_low < 0.05:
            continue                              # the low is reached in the first step
        order = {"company": "AAA", "action": "buy", "price": round((candle_low + step1_low) / 2, 4), "shares": 1}
        waiting, shares, _ = run_orders([order], ts, 1)
        assert waiting == [order] and shares["AAA"] == 0, f"filled with a future price on {ts}"
        checked += 1
    assert checked > 10                           # the situation really was tested


def test_sell_reached_during_this_step_is_filled(ts):
    _, high = cs.step_price_range("AAA", ts, 3, 4)
    order = {"company": "AAA", "action": "sell", "price": round(high - 0.01, 4), "shares": 5}
    waiting, shares, _ = run_orders([order], ts, 3, shares={"AAA": 5, "BBB": 0})
    assert waiting == [] and shares["AAA"] == 0


def test_portfolio_is_valued_at_the_price_now(ts):
    _, _, values = run_orders([], ts, 2, shares={"AAA": 10, "BBB": 0})
    assert values["AAA"] == pytest.approx(10 * cs.current_price("AAA", ts, 2, 4))


def test_market_price_button_gives_the_price_now_not_the_future_close(ts, real_candle):
    price = request.fill_market_price(1, "AAA", ts, 1, 4)
    assert price == round(cs.current_price("AAA", ts, 1, 4), 2)
    assert request.fill_market_price(1, "AAA", ts, 4, 4) == round(real_candle("AAA", ts)[3], 2)
