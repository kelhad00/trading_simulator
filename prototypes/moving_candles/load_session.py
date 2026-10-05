"""Read a TradeSim session.zip without writing anything to disk.

TradeSim's own loader (trade/utils/session.py -> extract_session_zip) copies the
CSVs into Data/, which would overwrite the simulator's data. This prototype must
not touch Data/, so everything here is read from the zip in memory.
"""
import io
import json
import zipfile

import pandas as pd

OHLC = ["Open", "High", "Low", "Close"]


class Session:
    """Settings and market data from one session.zip."""

    def __init__(self, stores, market):
        self.stores = stores      # the "stores" dict from session.json
        self.market = market      # DataFrame, columns = (ticker, field), as in TradeSim

    @property
    def companies(self):
        """{ticker: label} for the session's companies that have price data in the file."""
        info = self.stores.get("companies", {})
        in_file = set(self.market.columns.get_level_values(0))
        # Same companies as the session in TradeSim; all tickers in the file if it lists none
        tickers = [t for t in info if t in in_file] or sorted(in_file)
        return {t: info.get(t, {}).get("label", t) for t in tickers if not self.candles(t).empty}

    def candles(self, ticker):
        """Finished daily candles for one company (rows without data removed)."""
        df = self.market[ticker]
        if not set(OHLC).issubset(df.columns):
            return pd.DataFrame(columns=OHLC)
        return df[OHLC].dropna().astype(float)


def load_session(source):
    """Load a session.zip from a file path or raw bytes. Nothing is written to disk."""
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)

    with zipfile.ZipFile(source, "r") as zf:
        names = zf.namelist()
        if "session.json" not in names:
            raise ValueError("Invalid session file: missing session.json")
        if "generated_data.csv" not in names:
            raise ValueError("Invalid session file: missing generated_data.csv")

        stores = json.loads(zf.read("session.json"))["stores"]
        # Same read options as TradeSim (trade/utils/market.py)
        market = pd.read_csv(io.BytesIO(zf.read("generated_data.csv")), header=[0, 1], index_col=0)

    # Dates mix +01:00 / +02:00 (summer time), so parse as UTC then show Paris time
    market.index = pd.to_datetime(market.index, utc=True).tz_convert("Europe/Paris")
    return Session(stores, market)
