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

def random_file():
    '''
    Function get a random file from the data path
    '''

    DATA_PATH = os.path.join(dlt.data_path, 'patterns')

    # Folder list
    folders = glob.glob(DATA_PATH + '/*')

    # Random folder
    random_folder = random.choice(folders)

    # File list
    files = glob.glob(random_folder + '/*')

    # Random file
    random_file = random.choice(files)

    return random_file


def calculate_market_change(df):
    '''
    NOT USED
    Convert the market data into percentage change compared to the open price
    '''

    # Check if the DataFrame contains the required columns
    if not {'Open', 'High', 'Low', 'Close'}.issubset(df.columns):
        raise ValueError("The DataFrame must contain the columns ['Open', 'High', 'Low', 'Close']")
    
    
    # Create a new column & Calculate the percentage of change
    df['Percentage Change'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    
    return df