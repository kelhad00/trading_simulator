"""When a news article appears during a session.

Every article belongs to the candle of its date (as set by `delta` when the news
was generated) and appears at a step inside that candle, never earlier:

- the article has its own time of day (e.g. 10:30 in a daily candle): the step
  that has reached that time (10:30 = 44% of the day -> step 2 of 4);
- otherwise (dated at the very start of its candle, as generated news is): a
  step picked from its title, the same for every participant;
- moving candles off (1 step): when its candle appears.

A position is (candle number, step); positions are compared like dates.
"""
import math
import zlib

import numpy as np
import pandas as pd

from trade.utils.candle_steps import normalize

_candle_cache = {}


def candle_starts(market_index):
    """Start of each candle as plain (wall-clock) times, like the news dates."""
    key = (id(market_index), len(market_index))
    if key not in _candle_cache:
        _candle_cache.clear()
        _candle_cache[key] = np.array([pd.Timestamp(t).replace(tzinfo=None) for t in market_index],
                                      dtype="datetime64[ns]")
    return _candle_cache[key]


def _article_step(offset, candle_length, title, n_steps):
    if n_steps == 1:
        return 1
    if offset > pd.Timedelta(0) and candle_length > pd.Timedelta(0):
        return min(max(math.ceil(offset / candle_length * n_steps), 1), n_steps)
    return 1 + zlib.crc32(str(title).encode()) % n_steps


def article_positions(news_df, market_index, steps_per_candle, title_column="title"):
    """(candle number, step) at which each article appears; Series aligned with news_df."""
    _, n_steps = normalize(None, steps_per_candle)
    starts = candle_starts(market_index)
    if len(starts) == 0:
        return pd.Series([(0, 1)] * len(news_df), index=news_df.index, dtype=object)
    lengths = np.diff(starts)
    typical = lengths[0] if len(lengths) else np.timedelta64(1, "D")

    dates = news_df["date"].to_numpy(dtype="datetime64[ns]")
    candle = np.searchsorted(starts, dates, side="right") - 1          # last candle starting at/before the date
    positions = []
    for c, d, title in zip(candle, dates, news_df[title_column]):
        if c < 0:                                                      # before the data starts: always visible
            positions.append((-1, 1))
            continue
        length = lengths[c] if c < len(lengths) else typical
        step = _article_step(pd.Timedelta(d - starts[c]), pd.Timedelta(length), title, n_steps)
        positions.append((int(c), step))
    return pd.Series(positions, index=news_df.index, dtype=object)


def now_position(market_index, timestamp, candle_step, steps_per_candle, candles_ahead=0):
    """Where the session is now, as (candle number, step). `candles_ahead` looks
    further ahead (the 'warn me X days early' notification setting)."""
    step, _ = normalize(candle_step, steps_per_candle)
    starts = candle_starts(market_index)
    current = pd.Timestamp(timestamp).replace(tzinfo=None).to_datetime64()
    candle = int(np.searchsorted(starts, current, side="right") - 1)
    return (candle + int(candles_ahead or 0), step)


def visible(positions, now):
    """Which articles have appeared by `now` (boolean Series)."""
    return positions.map(lambda p: tuple(p) <= tuple(now))
