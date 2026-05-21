import pandas as pd
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


