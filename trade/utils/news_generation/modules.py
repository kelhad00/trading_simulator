import pandas as pd
import random

def load_data(data_path, separator=';'):
    '''
    Load the data from a csv file separated by <separator>
    '''

    return pd.read_csv(data_path, sep=separator)


def save_data(data, data_path, separator=';'):
    '''
    Save the data in a csv file separated by <separator>
    '''

    data.to_csv(data_path, sep=separator, index=False)


def find_sector_for_company(company, activities):
    for sector, companies in activities.items():
        if company in companies:
            return sector
    return None


def random_number(data_size):
    '''
    Function to generate a random number between 1 and the length of the data
    '''

    return random.randint(1, data_size)


def percentage_change(previous, actual):
    '''
    Calculate the percentage change between two values
    '''
    try:
        if previous == 0:
            return 0.0
        result = ((actual - previous) / previous) * 100
        # NaN != NaN is True — catches numpy/pandas NaN without extra imports
        if result != result:
            return 0.0
        return result
    except (TypeError, ValueError):
        return 0.0