"""Moving candles: show each candle forming step by step, like TradingView.

With `steps-per-candle` = 4 a candle updates at 15, 30 and 45 min (of a 1 h
candle) and closes at 60 min. With 1 the candle appears finished, as before.

The market data only has the final Open/High/Low/Close of each candle, so the
price path inside a candle is generated:

    up candle   (Close >= Open):  Open -> Low  -> High -> Close
    down candle (Close <  Open):  Open -> High -> Low  -> Close

with a little seeded noise, always inside the real High/Low. After the last
step the candle is exactly the one in the file. The seed depends on the
company and the date, so every participant sees the same path.

`step` follows the "candle-step" store: 1..n = the candle at `timestamp` is
at that step, n (or None) = it is closed.
"""
import math
import zlib
from functools import lru_cache

import numpy as np
import pandas as pd

from trade.utils.market import get_market_dataframe

TICKS_PER_STEP = 15  # points of the generated path per step (like minutes)


def _path(o, h, l, c, n_steps, seed):
    """Generated price path inside one candle: n_steps * TICKS_PER_STEP + 1 points."""
    n = n_steps * TICKS_PER_STEP
    rng = np.random.default_rng(seed)

    if h == l:  # flat candle, nothing moves
        return np.full(n + 1, o)

    first, second = (l, h) if c >= o else (h, l)
    # When the two extremes are reached (as a share of the candle's time)
    t1 = rng.uniform(0.15, 0.45)
    t2 = rng.uniform(t1 + 0.15, 0.85)
    i1, i2 = round(t1 * n), round(t2 * n)

    path = np.concatenate([
        np.linspace(o, first, i1 + 1)[:-1],
        np.linspace(first, second, i2 - i1 + 1)[:-1],
        np.linspace(second, c, n - i2 + 1),
    ])
    noise = rng.normal(0, (h - l) * 0.04, n + 1)
    path = np.clip(path + noise, l, h)
    # Pin the points that must be exact
    path[0], path[i1], path[i2], path[-1] = o, first, second, c
    return path


@lru_cache(maxsize=4096)
def _steps(o, h, l, c, n_steps, seed):
    """Per step: (open, high so far, low so far, price now, low of this step, high of this step)."""
    path = _path(o, h, l, c, n_steps, seed)
    out = []
    for k in range(1, n_steps + 1):
        seen = path[: k * TICKS_PER_STEP + 1]
        segment = path[(k - 1) * TICKS_PER_STEP: k * TICKS_PER_STEP + 1]
        out.append((o, float(seen.max()), float(seen.min()), float(seen[-1]),
                    float(segment.min()), float(segment.max())))
    # Last step is the real candle, exactly
    last = out[-1]
    out[-1] = (o, h, l, c, last[4], last[5])
    return tuple(out)


def normalize(step, n_steps):
    """(step, n_steps) with defaults applied: None or out-of-range step = closed candle."""
    n_steps = max(int(n_steps or 1), 1)
    if step is None or not 1 <= int(step) <= n_steps:
        return n_steps, n_steps
    return int(step), n_steps


def is_forming(step, n_steps):
    step, n_steps = normalize(step, n_steps)
    return step < n_steps


def _real_candle(company, timestamp):
    df = get_market_dataframe()
    try:
        row = df.loc[timestamp, company]
        o, h, l, c = (float(row[k]) for k in ("Open", "High", "Low", "Close"))
    except (KeyError, TypeError, ValueError):
        return None
    if any(math.isnan(v) for v in (o, h, l, c)):
        return None
    return o, h, l, c


def _seed(company, timestamp):
    return zlib.crc32(f"{company}|{timestamp}".encode())


def _step_values(company, timestamp, step, n_steps):
    real = _real_candle(company, timestamp)
    if real is None:
        return None
    step, n_steps = normalize(step, n_steps)
    if n_steps == 1:
        o, h, l, c = real
        return o, h, l, c, l, h
    return _steps(*real, n_steps, _seed(company, timestamp))[step - 1]


def partial_candle(company, timestamp, step, n_steps):
    """(open, high, low, close) of the candle at `timestamp` as shown at this step, or None."""
    values = _step_values(company, timestamp, step, n_steps)
    return None if values is None else values[:4]


def current_price(company, timestamp, step, n_steps):
    """Price right now: the forming candle's latest price (its close once closed)."""
    values = _step_values(company, timestamp, step, n_steps)
    return float("nan") if values is None else values[3]


def step_price_range(company, timestamp, step, n_steps):
    """(low, high) reached DURING the current step only; the whole candle when steps are off.

    Used to fill limit orders: an order placed now can only be reached by prices
    from now on, not by prices earlier in the candle.
    """
    values = _step_values(company, timestamp, step, n_steps)
    return (float("nan"), float("nan")) if values is None else values[4:6]


def step_minutes(step, n_steps):
    """Market minutes into a 1 h candle at this step (15, 30, 45, 60 with 4 steps)."""
    step, n_steps = normalize(step, n_steps)
    return round(60 * step / n_steps)


def market_time(timestamp, step, n_steps):
    """Timestamp for logs: the candle's date plus the minutes reached inside it.

    Unchanged when steps are off, so logs keep today's format for 1 step.
    """
    step, n_steps = normalize(step, n_steps)
    if n_steps == 1 or timestamp in (None, ""):
        return timestamp
    try:
        return str(pd.Timestamp(timestamp) + pd.Timedelta(minutes=step_minutes(step, n_steps)))
    except (ValueError, TypeError):
        return timestamp
