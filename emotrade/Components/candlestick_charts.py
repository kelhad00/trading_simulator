import plotly.graph_objects as go
import pandas as pd
import time

PLOTLY_CONFIG = {
    'displaylogo': False,
    'modeBarButtonsToRemove': ['toImage', 'select','lasso2d']
}

def create_graph(dataframe, timestamp='', next_graph=True, range=10):
    """
    Create a candlestick chart for the selected stock or update an existing one

    Parameters
    ----------
    dataframe : str
        dataframe containing the market data

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

    # if this is the first time the graph is being created
    if (timestamp == ''):
        if range == 0:
            dftmp = dataframe[:1]
        else:
            dftmp = dataframe[:range]
    else: # if the graph is being updated
        idx = dataframe.index.get_loc(timestamp) + 1
        if idx == 1: # if the timestamp is the first element of the dataframe
            if range == 0:
                dftmp = dataframe[:1]
            else:
                dftmp = dataframe[:range]
        elif next_graph: # You want to see the graph with new data
            if range == 0 or idx < range:
                dftmp = dataframe.iloc[:idx + 1]
            else:
                dftmp = dataframe.iloc[idx - (range - 1) : idx + 1]
        else: # You want to see the graph of another company
              # And so with the same timestamp as the previous graph
            if range == 0:
                dftmp = dataframe.iloc[: idx]
            else:
                dftmp = dataframe.iloc[idx - range : idx]

    #creating the plot the long moving average
    long_mov_av = go.Scatter(
        x = dftmp.index,
        y = dftmp['long_MA'],
        name = 'longMA'
    )

    #creating the plot the short moving average
    short_mov_av = go.Scatter(
        x = dftmp.index,
        y = dftmp['short_MA'],
        name = 'shortMA'
    )

    #creating the plot the candlestick plot
    candelstick = go.Candlestick(
        x = dftmp.index,
        open  = dftmp['Open'],
        high  = dftmp['High'],
        low   = dftmp['Low'],
        close = dftmp['Close'],
        name = 'price',
        showlegend = False
    )

    # Create chart for the selected stock
    figure = go.Figure(data = [long_mov_av, short_mov_av, candelstick])

    return figure, dftmp.index[-1]


if __name__ == '__main__':
    import os

    name = 'MC.PA'

    file_path = os.path.join('Data' , 'market_data.csv')
    df = pd.read_csv(file_path, header=[0,1],index_col=0)[name]

    fig, endtime = create_graph(df)
    fig.show(config=PLOTLY_CONFIG)

    testtime = 3
    while testtime > 0:
        time.sleep(5)

        fig,endtime = create_graph(df, endtime)
        print(endtime)

        fig.show(config=PLOTLY_CONFIG)

        testtime -= 1