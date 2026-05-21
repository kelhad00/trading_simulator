import os
import pandas as pd

from trade.defaults import defaults as dlt

# mtime-based caches — key is filename, value is (mtime, dataframe)
_market_cache: dict = {}
_revenues_cache: list = [None, -1.0]


def get_revenues_dataframe():
    file_path = os.path.join(dlt.data_path, 'revenue.csv')
    try:
        mtime = os.path.getmtime(file_path)
        if _revenues_cache[0] is not None and _revenues_cache[1] == mtime:
            return _revenues_cache[0]
        df = pd.read_csv(file_path, index_col=0, header=[0, 1])
        _revenues_cache[0] = df
        _revenues_cache[1] = mtime
        return df
    except Exception:
        raise


def get_market_dataframe(generated=True):
    file = 'generated_data.csv' if generated else 'market_data.csv'
    file_path = os.path.join(dlt.data_path, file)
    try:
        mtime = os.path.getmtime(file_path)
        cached = _market_cache.get(file)
        if cached is not None and cached[0] == mtime:
            return cached[1]
        df = pd.read_csv(file_path, index_col=0, header=[0, 1])
        _market_cache[file] = (mtime, df)
        return df
    except Exception:
        print('ERROR: No market data found in ' + dlt.data_path + ' folder.')
        return None


def get_price_dataframe():
    df = get_market_dataframe()
    price_list = df.xs('Close', axis=1, level=1)
    return price_list


def get_first_timestamp(market_df, range=0):
    try:
        timestamp = market_df.index[range]
        return timestamp
    except Exception:
        return 0


def get_last_timestamp(market_df):
    try:
        timestamp = market_df.index[-1]
        return timestamp
    except Exception:
        return 0
