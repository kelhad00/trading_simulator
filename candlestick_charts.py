import plotly.graph_objects as go
import pandas as pd
import time
import os

PLOTLY_CONFIG = {
    'displaylogo': False,
    'modeBarButtonsToRemove': ['toImage', 'select','lasso2d']
}

def create_next_graph(company_id, timestamp='', range=10):
    """
    Create a candlestick chart for the selected stock or update an existing one

    Parameters
    ----------
    company_id : str
        NASDAQ stock name

    timestamp : str
        timestamp of the initial market data to display (optional)
        if not specified, the oldest market data will be displayed

    range : int
        number of data points to display (default: 10)

    Returns
    -------
    plotly.graph_objects.Figure
        Candlestick chart to display

    datetime.datetime
        Last timestamp of the default market data used to create the chart
    """

    # Get saved market data
    file_path = os.path.join('market_data' , company_id + '.csv')
    df = pd.read_csv(file_path, index_col=0)

    # if this is the first time the graph is being created
    if (timestamp == ''):
        if range == 0:
            dftmp = df[:1]
        else:
            dftmp = df[:range]
    else: # if the graph is being updated
        idx = df.index.get_loc(timestamp)
        if range == 0:
            dftmp = df.iloc[:idx + 1]
        else:
            dftmp = df.iloc[idx - (range - 2) : idx + 2]

     # Create candlestick chart for the selected stock
    figure = go.Figure(
        data = [go.Candlestick(
            x = dftmp.index,
            open  = dftmp['Open'],
            high  = dftmp['High'],
            low   = dftmp['Low'],
            close = dftmp['Close']
        )]
    )

    # Define chart layout
    figure.update_layout(
        #title = company_id + ' stock price',
        xaxis_title = 'Date',
        yaxis_title = 'Price',
        yaxis_tickprefix = '€',
        showlegend=False
    )

    return figure, dftmp.index[-1]


#TODO: Deprecated. Remove this function
def create_candlestick_chart(company_id, timestamp='', range=10):
    """
    Create a candlestick chart for the selected stock

    Parameters
    ----------
    company_id : str
        NASDAQ stock name

    timestamp : str
        timestamp of the initial market data to display (optional)
        if not specified, the oldest market data will be displayed

    range : int
        number of data points to display (default: 10)

    Returns
    -------
    plotly.graph_objects.Figure
        Candlestick chart for the selected stock

    pandas.DataFrame
        Saved market data for the selected stock

    datetime.datetime
        Last timestamp of the default market data used to create the chart
    """

    # Get saved market data
    file_path = os.path.join('market_data' , company_id + '.csv')
    df = pd.read_csv(file_path, index_col=0)

    # Select market data to display depending on the range and the timestamp
    if (timestamp == ''):
        if range == 0:
            dftmp = df[:1]
        else:
            dftmp = df[:range]
    else:
        if range == 0:
            dftmp = df[timestamp-1:timestamp]
        else:
            dftmp = df[:timestamp]

    # Create candlestick chart for the selected stock
    figure = go.Figure(
        data = [go.Candlestick(
            x = dftmp.index,
            open  = dftmp['Open'],
            high  = dftmp['High'],
            low   = dftmp['Low'],
            close = dftmp['Close']
        )]
    )

    # Define chart layout
    figure.update_layout(
        #title = company_id + ' stock price',
        xaxis_title = 'Date',
        yaxis_title = 'Price',
        yaxis_tickprefix = '€',
        showlegend=False
    )


    return figure, df, dftmp.index[-1]


#TODO: Deprecated. Remove this function
def update_candlestick_chart(figure, dataframe, lasttimestamp, range = 10):
    """
    Update the candlestick chart with new market data

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        Candlestick chart for the selected stock to update

    dataframe : pandas.DataFrame
        Saved market data for the selected stock

    lasttimestamp : datetime.datetime
        Timestamp used to display the last iteration of the candlestick chart

    range : int
        number of data points to display (default: 10)

    Returns
    -------
    datetime.datetime
        Timestamp used to display the new iteration of the candlestick chart
    """

    idx = dataframe.index.get_loc(lasttimestamp)

    if (range == 0):
        # Apprend new data indefinitely
        newdata = dataframe.iloc[idx+1]

        figure.add_trace( go.Candlestick(
                x = [newdata.name],
                open  = [newdata['Open']],
                high  = [newdata['High']],
                low   = [newdata['Low']],
                close = [newdata['Close']],
        ))

        return  newdata.name

    else :
        # Append new data with a fixed range
        dftmp = dataframe.iloc[idx - (range - 2) : idx + 2]

        figure.update_traces(go.Candlestick(
                x = dftmp.index,
                open  = dftmp['Open'],
                high  = dftmp['High'],
                low   = dftmp['Low'],
                close = dftmp['Close']
        ))

        return dftmp.index[-1]


if __name__ == '__main__':
    name = 'TSLA'

    fig,endtime = create_next_graph(name)
    fig.show()

    testtime = 3
    while testtime > 0:
        time.sleep(5)

        fig,endtime = create_next_graph(name, endtime)
        print(endtime)

        fig.show()
        testtime -= 1