import os.path

import numpy as np
import pandas as pd
from trade.utils.settings.data_handler import scale_market_data, random_number, load_data, random_file, get_pattern_file

from trade.defaults import defaults as dlt


def bull_trend(data, data_size, alpha=500, length=100):
    # Parameters
    # alpha: the difference between the close price at the start and end of the trend
    # length: the length of the trend

    '''
    Found a bull trend in the market data and return the index of the trend
    '''

    rand = 0
    i = 0
    while True:
        rand = random_number(data_size - length - 1)
        i += 1

        if data['Close'].iloc[rand] < data['Close'].iloc[rand + length] and (data['Close'].iloc[rand + length] - data['Close'].iloc[rand] >= alpha):
            break

        if i > 1000:
            raise Exception("No bull trend found")

    # Return the index of the trend
    return rand


def bear_trend(data, data_size, alpha=500, length=100):
    # Parameters
    # alpha: the difference between the close price at the start and end of the trend
    # length: the length of the trend

    '''
    Found a bear trend in the market data and return the index of the trend
    '''

    rand = 0
    i = 0
    while True:
        rand = random_number(data_size - length - 1)
        i += 1

        if data['Close'].iloc[rand] > data['Close'].iloc[rand + length] and (data['Close'].iloc[rand] - data['Close'].iloc[rand + length] >= alpha):
            break

        if i > 1000:
            raise Exception("No bear trend found")

    # Return the index of the trend
    return rand


def flat_trend(data, data_size, alpha=50, length=100):
    # Parameters
    # alpha: the maximum difference between the close price at the start and end of the trend
    # length: the length of the trend

    '''
    Found a flat trend in the market data and return the index of the trend
    '''

    rand = 0
    i = 0
    while True:
        rand = random_number(data_size - length - 1)
        i += 1

        # Calculate the standard deviation
        std = np.std(data['Close'].iloc[rand:rand + length])

        if abs(data['Close'].iloc[rand] - data['Close'].iloc[rand + length]) <= alpha and std <= 80:
            break

        if i > 1000:
            raise Exception("No flat trend found")

    # Return the index of the trend
    return rand


def add_pattern(chart, nbr_pattern):
    '''
    Add patterns to the chart and return the final chart
    '''

    final_chart = chart

    # Split the chart into n parts
    split_chart = np.array_split(final_chart, nbr_pattern)

    # Add pattern to the chart
    for i in range(nbr_pattern):

        # Get a random pattern
        random_file_path = random_file()

        # Load the pattern
        pattern = load_data(random_file_path)

        # Reset the index of the split chart
        split_chart[i] = split_chart[i].reset_index(drop=True)

        # Random position for the pattern
        position = random_number(split_chart[i].shape[0]-1)

        # Split the chart
        chart1 = split_chart[i].iloc[:position].reset_index(drop=True)
        chart2 = split_chart[i].iloc[position:].reset_index(drop=True)

        # Scale the pattern & the second part of the chart
        pattern = scale_market_data(pattern, split_chart[i].at[position, 'Close'])
        last_close = pattern.at[pattern.shape[0] - 1, 'Close']
        chart2 = scale_market_data(chart2, last_close)

        # Concatenate the data
        split_chart[i] = pd.concat([chart1, pattern, chart2]).reset_index(drop=True)

    # Concatenate the n parts
    final_chart = pd.concat(split_chart).reset_index(drop=True)

    return final_chart


def _apply_hamming_taper(df, taper_pct=0.10):
    """
    Compress OHLC candle spread at pattern entry and exit using a Hamming ramp.

    At the boundary (w=0) each candle collapses to its Open price (flat doji).
    At the interior (w=1) candles retain their full shape.  This prevents
    the abrupt volatility jump that otherwise appears where the pattern is
    spliced into the surrounding segment.
    """
    df = df.copy().reset_index(drop=True)
    n = len(df)
    taper_n = max(3, int(n * taper_pct))
    cols = [c for c in ('High', 'Low', 'Close', 'Adj Close') if c in df.columns]

    for i in range(taper_n):
        w = 0.5 * (1 - np.cos(np.pi * i / max(taper_n - 1, 1)))  # 0 → 1

        mid = df.at[i, 'Open']                          # entry
        for col in cols:
            df.at[i, col] = mid + w * (df.at[i, col] - mid)

        j = n - 1 - i                                   # exit (mirror)
        if j != i:
            mid = df.at[j, 'Open']
            for col in cols:
                df.at[j, col] = mid + w * (df.at[j, col] - mid)

    return df


def inject_pattern(segment, pattern_type):
    """
    Inject a specific technical pattern into a market data segment.

    pattern_type must match a folder name under Data/patterns/ (e.g. "double_top").
    The pattern is tapered in/out with a Hamming window to smooth the splice.
    Returns the segment unchanged if no pattern file is found.
    """
    path = get_pattern_file(pattern_type)
    if path is None:
        return segment

    pattern = load_data(path)
    segment = segment.reset_index(drop=True)
    n = segment.shape[0]

    if n < 3:
        return segment

    position = np.random.randint(1, n - 1)

    chart1 = segment.iloc[:position].reset_index(drop=True)
    chart2 = segment.iloc[position:].reset_index(drop=True)

    pattern = scale_market_data(pattern, segment.at[position, 'Close'])
    pattern = _apply_hamming_taper(pattern)

    last_close = pattern.at[pattern.shape[0] - 1, 'Close']
    chart2 = scale_market_data(chart2, last_close)

    return pd.concat([chart1, pattern, chart2]).reset_index(drop=True)


def apply_event_overlay(df, event_type, position_pct, magnitude_pct):
    """
    Overlay a localised event curve on the final chart.

    Formula (supervisor):  y(t) = close(t) * event_curve(t)  for t >= event_start

    event_curve is 1.0 before the event, then rises/falls smoothly using a
    half-cosine (Hamming-shaped) ramp so the transition has no abrupt kink.

    Parameters
    ----------
    event_type    : 'crash' or 'rally'
    position_pct  : 0–100, where in the chart the event begins
    magnitude_pct : 0–100, depth (crash) or height (rally) as % of price
    """
    if event_type not in ('crash', 'rally'):
        return df

    df = df.copy().reset_index(drop=True)
    n = len(df)
    event_idx = max(1, min(n - 2, int(n * position_pct / 100)))
    post_len  = n - event_idx
    if post_len < 2:
        return df

    magnitude = magnitude_pct / 100.0
    t_post    = np.arange(post_len) / max(post_len - 1, 1)
    ramp      = 0.5 * (1 - np.cos(np.pi * t_post))       # smooth 0 → 1

    event_curve = np.ones(n)
    if event_type == 'crash':
        event_curve[event_idx:] = 1.0 - magnitude * ramp
    else:
        event_curve[event_idx:] = 1.0 + magnitude * ramp

    for col in ('Open', 'High', 'Low', 'Close', 'Adj Close'):
        if col in df.columns:
            df[col] = df[col] * event_curve

    # Light smoothing on Close to erase the kink at the event boundary
    df['Close'] = (
        pd.Series(df['Close'])
        .rolling(3, center=True, min_periods=1)
        .mean()
        .values
    )

    # Restore OHLC consistency after the multiplier
    df['High'] = np.maximum(df['High'], df['Close'])
    df['Low']  = np.minimum(df['Low'],  df['Close'])
    df['Low']  = np.maximum(df['Low'], 0.1)

    return df


def get_generated_data():
    file_path = os.path.join(dlt.data_path, 'generated_data.csv')
    try:
        existing_df = pd.read_csv(file_path, index_col=0, header=[0, 1])
    except Exception as e:
        print('ERROR: No generated data found in ' + dlt.data_path + ' folder.')
        existing_df = None

    return existing_df

def delete_generated_data(stock):
    '''
    Delete a specific stock in generated data csv
    '''

    existing_df = get_generated_data()
    if existing_df is not None:
        symbols = existing_df.columns.get_level_values('symbol').unique()
        if stock in symbols:
            existing_df = existing_df.drop(stock, axis=1, level='symbol')

    file_path = os.path.join(dlt.data_path, 'generated_data.csv')
    existing_df.to_csv(file_path, index=True)

    return None


def format_generated_data(data, stock):
    '''
    Format the generated data
    '''


    data.set_index('Date', inplace=True)
    data.index.name = 'date'
    data.index = pd.to_datetime(data.index, utc=True)
    data.index = data.index.tz_convert('Europe/Paris')

    # Ensure there are at least 20 non-NaN values in the 'Close' column
    if data['Close'].dropna().shape[0] < 20:
        print("Not enough non-NaN values to compute the rolling mean")

    # Compute the rolling mean for 'long_MA'
    data['long_MA'] = data['Close'].rolling(window=20, min_periods=1).mean()
    data['short_MA'] = data['Close'].rolling(window=50, min_periods=1).mean()
    data['200_MA'] = data['Close'].rolling(window=200, min_periods=1).mean()

    # data['long_MA'] = data['Close'].rolling(int(20)).mean()
    # data['short_MA'] = data['Close'].rolling(int(50)).mean()
    # data['200_MA'] = data['Close'].rolling(int(200)).mean()



    #rename col Adj Close to adjclose
    data.rename(columns={'Adj Close': 'adjclose'}, inplace=True)

    columns = pd.MultiIndex.from_tuples(
        [(stock, col) for col in data.columns],
        names=['symbol', None]
    )

    df = pd.DataFrame(index=data.index, columns=columns)

    for col in data.columns:
        df.loc[:, (stock, col)].update(data[col])



    return df




def export_generated_data(df, stock):
    '''
    Export the generated data
    '''

    data = df.copy()
    df = format_generated_data(data, stock)
    existing_df = get_generated_data()

    if existing_df is not None:
        existing_df.index = pd.to_datetime(existing_df.index, utc=True)
        existing_df.index = existing_df.index.tz_convert('Europe/Paris')

        symbols = existing_df.columns.get_level_values('symbol').unique()
        if stock in symbols:
            print('Stock already exists in the generated data')
            existing_df = existing_df.drop(stock, axis=1, level='symbol')

    combined_df = pd.concat([existing_df, df], axis=1)


    file_path = os.path.join(dlt.data_path, 'generated_data.csv')
    combined_df.to_csv(file_path, index=True)

    return None

