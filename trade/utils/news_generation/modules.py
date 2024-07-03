import pandas as pd


def load_data(data_path):
    '''
    Load the data
    ['date', 'ticker', 'sector', 'title', 'content']
    '''

    return pd.read_csv(data_path, sep=';')


def save_data(data, data_path):
    '''
    Save the data in a csv file
    ['date', 'ticker', 'sector', 'title', 'content']
    '''

    data.to_csv(data_path, sep=';', index=False)