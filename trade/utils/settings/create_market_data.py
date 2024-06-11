import numpy as np
import pandas as pd
from trade.utils.settings.data_handler import scale_market_data, random_number, load_data, random_file


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