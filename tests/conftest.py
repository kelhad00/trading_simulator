"""Shared set-up for the tests.

The tests never use the real data folder: the `fake_data` fixture writes a small
invented dataset (2 companies, 160 days, a few news items) into a temporary
folder and points the app at it. So the tests work on any computer and can't
change real data.

Run all tests from the trading_simulator folder:
    .\\trade\\venv\\Scripts\\python.exe -m pytest
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # trading_simulator
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("LOG_LEVEL", "WARNING")   # keep test output readable

from trade.defaults import defaults as dlt                      # noqa: E402
from trade.utils import market, news as news_utils, candle_steps  # noqa: E402

N_DAYS = 160          # more than the default 100 history candles
SHORT_DAYS = 120      # BBB has less data: its last 40 days are empty


def _clear_caches():
    market._market_cache.clear()
    news_utils._news_cache[0], news_utils._news_cache[1] = None, -1.0
    candle_steps._steps.cache_clear()


def _make_prices(seed, n):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    open_ = close + rng.normal(0, 0.8, n)
    high = np.maximum(open_, close) + rng.uniform(0.1, 2, n)
    low = np.minimum(open_, close) - rng.uniform(0.1, 2, n)
    s = pd.Series(close)
    return {"Open": open_, "High": high, "Low": low, "Close": close,
            "short_MA": s.rolling(20).mean().values, "long_MA": s.rolling(50).mean().values,
            "200_MA": s.rolling(200).mean().values}


@pytest.fixture
def fake_data(tmp_path, monkeypatch):
    """A tiny made-up data folder; the app reads it instead of the real one."""
    dates = [str(d) for d in pd.date_range("2025-01-01", periods=N_DAYS, freq="D", tz="Europe/Paris")]
    frames = {}
    for ticker, seed in (("AAA", 1), ("BBB", 2)):
        df = pd.DataFrame(_make_prices(seed, N_DAYS), index=dates)
        if ticker == "BBB":
            df.iloc[SHORT_DAYS:] = np.nan                       # a company with less data
        frames[ticker] = df
    data = pd.concat(frames, axis=1)
    data.columns.names = ["symbol", None]
    data.index.name = "date"
    data.to_csv(tmp_path / "generated_data.csv")

    news = pd.DataFrame([
        ("10/01/25 09:00", "AAA", "Tech", "AAA beats expectations", "Strong quarter.", "positive", "strong positive"),
        ("11/01/25 09:00", "AAA", "Tech", "AAA warns on costs", "Margins down.", "negative", "weak negative"),
        ("12/01/25 09:00", "BBB", "Energy", "BBB keeps guidance", "No change.", "positive", "no positive"),
        ("13/01/25 09:00", "BBB", "Energy", "BBB routine update", "Routine.", "negative", ""),
        ("14/01/25 09:00", "AAA", "Tech", "AAA efficiency drive", "Cost cuts.", "positive", "strong negative"),
    ], columns=["date", "ticker", "sector", "title", "content", "sentiment", "sentiment_label"])
    news.to_csv(tmp_path / "news.csv", sep=";", index=False)

    monkeypatch.setattr(dlt, "data_path", str(tmp_path))
    _clear_caches()
    yield tmp_path
    _clear_caches()


@pytest.fixture
def market_df(fake_data):
    return market.get_market_dataframe()


@pytest.fixture
def real_candle(market_df):
    """(o, h, l, c) of a company at a date, straight from the fake file."""
    def get(ticker, ts):
        row = market_df.loc[ts, ticker]
        return tuple(float(row[k]) for k in ("Open", "High", "Low", "Close"))
    return get
