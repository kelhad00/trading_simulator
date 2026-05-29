import pandas as pd
import numpy as np
import random
import glob
import os

from trade.defaults import defaults as dlt


def scale_market_data(df, previous_close):
    '''
    Function to scale the market data based on the previous close price
    '''

    # Calculate the scale factor
    scale_factor = previous_close / df.at[0, 'Open']
    
    # Scale the data
    df_scaled = df.copy()
    df_scaled[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']] * scale_factor

    # Return the scaled data
    return df_scaled


def load_data(data_path):
    '''
    Function to load the data from a CSV file
    '''

    return pd.read_csv(data_path).dropna()


def get_data_size(data):
    '''
    Function to get the size of the dataframe
    '''

    return data.shape[0]


def random_number(data_size):
    '''
    Function to generate a random number between 1 and the length of the data
    '''

    return random.randint(1, data_size)

def normalize_to_volatility(segment, prev_close, target_daily_vol):
    """
    Anchor the segment to prev_close, then rescale internal price deviations
    so the pattern's daily Close return std matches target_daily_vol.

    This prevents patterns with high or low source volatility from creating
    unrealistic spikes or flat spots in the generated chart.
    """
    segment = segment.copy().reset_index(drop=True)

    # Step 1: anchor start price to prev_close (same as scale_market_data)
    anchor = prev_close / segment.at[0, 'Open']
    for col in ('Open', 'High', 'Low', 'Close'):
        if col in segment.columns:
            segment[col] = segment[col] * anchor

    # Step 2: measure the pattern's own daily return volatility after anchoring
    returns = segment['Close'].pct_change().dropna()
    pattern_vol = returns.std()

    if pattern_vol > 1e-8 and target_daily_vol > 1e-8:
        # Cap amplitude factor at 3× to avoid extreme compression/expansion
        amp_factor = min(target_daily_vol / pattern_vol, 3.0)

        # Step 3: rescale deviations from prev_close for all price columns
        for col in ('Open', 'High', 'Low', 'Close'):
            if col in segment.columns:
                segment[col] = prev_close + (segment[col] - prev_close) * amp_factor

    # Step 4: restore OHLC consistency and floor prices above zero
    segment['Low']  = np.maximum(segment['Low'], 0.1)
    segment['High'] = np.maximum(segment['High'], segment[['Open', 'Close']].max(axis=1))
    segment['Low']  = np.minimum(segment['Low'],  segment[['Open', 'Close']].min(axis=1))

    # Keep Adj Close in sync with Close (pattern CSVs set them equal anyway)
    if 'Adj Close' in segment.columns:
        segment['Adj Close'] = segment['Close']

    return segment


def get_pattern_file_excluding(pattern_type, used_paths):
    """
    Return a random CSV from pattern_type folder that is not in used_paths.
    Falls back to any available file if all have been used (avoids hard failure).
    Returns None if the folder is missing or empty.
    """
    folder = os.path.join(dlt.data_path, 'patterns', pattern_type)
    all_files = glob.glob(folder + '/*.csv')
    if not all_files:
        return None
    available = [f for f in all_files if f not in used_paths]
    return random.choice(available if available else all_files)


