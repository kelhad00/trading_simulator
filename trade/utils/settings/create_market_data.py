import os.path

import numpy as np
import pandas as pd
from trade.utils.settings.data_handler import scale_market_data, random_number, load_data, random_file

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
    print("copy", df)
    df = format_generated_data(data, stock)
    existing_df = get_generated_data()

    existing_df.index = pd.to_datetime(existing_df.index, utc=True)
    existing_df.index = existing_df.index.tz_convert('Europe/Paris')


    if existing_df is not None:
        symbols = existing_df.columns.get_level_values('symbol').unique()
        if stock in symbols:
            print('Stock already exists in the generated data')
            existing_df = existing_df.drop(stock, axis=1, level='symbol')


    # combined_df = existing_df[stock] = df
    print(df.index)
    print(existing_df.index)

    combined_df = pd.concat([existing_df, df], axis=1)


    file_path = os.path.join(dlt.data_path, 'generated_data.csv')
    combined_df.to_csv(file_path, index=True)

    return None

