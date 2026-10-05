"""Moving candles: a candle forms step by step (15/30/45 min) and ends on the real candle."""
import math

import pandas as pd
import pytest

from trade.utils import candle_steps as cs
from conftest import SHORT_DAYS


@pytest.mark.parametrize("n_steps", [2, 4, 12])
def test_last_step_is_exactly_the_real_candle(market_df, real_candle, n_steps):
    for ticker in ("AAA", "BBB"):
        for ts in market_df.index[:SHORT_DAYS]:
            assert cs.partial_candle(ticker, ts, n_steps, n_steps) == real_candle(ticker, ts)


@pytest.mark.parametrize("n_steps", [2, 4, 12])
def test_open_never_moves_high_only_rises_low_only_falls(market_df, real_candle, n_steps):
    for ts in market_df.index[:SHORT_DAYS]:
        o, h, l, c = real_candle("AAA", ts)
        prev_high, prev_low = -math.inf, math.inf
        for step in range(1, n_steps + 1):
            so, sh, sl, sc = cs.partial_candle("AAA", ts, step, n_steps)
            assert so == o
            assert sh >= prev_high and sl <= prev_low
            assert l <= sl <= sh <= h          # inside the real candle
            assert sl <= sc <= sh              # price now is between low and high so far
            prev_high, prev_low = sh, sl


def test_prices_never_leave_the_real_high_low(market_df, real_candle):
    for ts in market_df.index[:SHORT_DAYS]:
        o, h, l, c = real_candle("AAA", ts)
        for step in range(1, 5):
            lo, hi = cs.step_price_range("AAA", ts, step, 4)
            assert l <= lo <= hi <= h
            assert lo <= cs.current_price("AAA", ts, step, 4) <= hi


def test_off_setting_shows_the_finished_candle(market_df, real_candle):
    ts = market_df.index[110]
    o, h, l, c = real_candle("AAA", ts)
    assert cs.partial_candle("AAA", ts, 1, 1) == (o, h, l, c)
    assert cs.current_price("AAA", ts, 1, 1) == c
    assert cs.step_price_range("AAA", ts, 1, 1) == (l, h)      # whole candle, like before


def test_every_participant_sees_the_same_path(market_df):
    ts = market_df.index[110]
    first = [cs.partial_candle("AAA", ts, k, 4) for k in range(1, 5)]
    cs._steps.cache_clear()
    assert [cs.partial_candle("AAA", ts, k, 4) for k in range(1, 5)] == first


def test_company_without_data_on_that_day_has_no_forming_candle(market_df):
    ts = market_df.index[SHORT_DAYS + 5]                       # BBB's data has ended
    assert cs.partial_candle("BBB", ts, 2, 4) is None
    assert math.isnan(cs.current_price("BBB", ts, 2, 4))


@pytest.mark.parametrize("step, n_steps, expected", [
    (None, 4, (4, 4)),      # nothing stored yet = closed candle
    (9, 4, (4, 4)),         # out of range (setting changed) = closed candle
    (2, 4, (2, 4)),
    (1, None, (1, 1)),      # no setting = 1 step (off)
])
def test_normalize(step, n_steps, expected):
    assert cs.normalize(step, n_steps) == expected


def test_log_time_shows_the_minute_inside_the_candle():
    ts = "2025-06-10 00:00:00+02:00"
    times = [cs.market_time(ts, k, 4) for k in range(1, 5)]
    assert [pd.Timestamp(t).minute for t in times[:3]] == [15, 30, 45]
    assert pd.Timestamp(times[3]).hour == 1                   # 60 min = closed
    assert cs.market_time(ts, 1, 1) == ts                      # off: log format unchanged
