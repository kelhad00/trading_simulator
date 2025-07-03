import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

from trade.defaults import defaults as dlt

PLOTLY_CONFIG = {
    'displaylogo': False,
    'modeBarButtonsToRemove': ['toImage', 'select', 'lasso2d'],
    'modeBarButtonsToAdd': ['drawline'],
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
    if timestamp == '':
        if range == 0:
            dftmp = dataframe[:1]
        else:
            dftmp = dataframe[:range]

    else:  # if the graph is being updated
        idx = dataframe.index.get_loc(timestamp)
        # Correction : forcer idx à être un int si ce n'est pas le cas
        if isinstance(idx, slice):
            idx = idx.start
        elif isinstance(idx, (list, np.ndarray)):
            idx = idx[0]
        if idx == 0:  # if the timestamp is the first element of the dataframe
            if range == 0:
                dftmp = dataframe[:1]
            else:
                dftmp = dataframe[:range]
        elif next_graph:  # You want to see the graph with new data
            # The timestamp is already updated by the callback based on granularity
            # So we just need to show the data up to the current timestamp
            if range == 0 or idx < range:
                dftmp = dataframe.iloc[:idx + 1]
            else:
                dftmp = dataframe.iloc[idx - (range - 1): idx + 1]
        else:  # You want to see the graph of another company
            # And so with the same timestamp as the previous graph
            if range == 0 or idx < range:
                dftmp = dataframe.iloc[: idx]
            else:
                dftmp = dataframe.iloc[idx - range: idx]

    # creating the plot the long moving average
    long_mov_av = go.Scatter(
        x=dftmp.index,
        y=dftmp['long_MA'],
        name='longMA'
    )

    # creating the plot the short moving average
    short_mov_av = go.Scatter(
        x=dftmp.index,
        y=dftmp['short_MA'],
        name='shortMA'
    )

    # creating the plot the 200 moving average
    twohun_mov_av = go.Scatter(
        x=dftmp.index,
        y=dftmp['200_MA'],
        name='twohunMA'
    )

    # creating the plot the candlestick plot
    candelstick = go.Candlestick(
        x=dftmp.index,
        open=dftmp['Open'],
        high=dftmp['High'],
        low=dftmp['Low'],
        close=dftmp['Close'],
        name='price',
        showlegend=False
    )

    # Create chart for the selected stock
    figure = go.Figure(data=[long_mov_av, short_mov_av, twohun_mov_av, candelstick])

    # creating the plot the RSI plot
    rsi = calculate_rsi(dftmp['Close'])
    valid_idx = rsi.dropna().index
    figure.add_trace(go.Scatter(x=valid_idx, y=rsi.loc[valid_idx], name='RSI', yaxis="y2", line=dict(color='purple')))


    # Ajout des zones de sur-achat et de sur-vente
    figure.add_shape(type="rect", xref="paper", yref="y2",
                  x0=0, y0=70, x1=1, y1=100,
                  fillcolor="pink", opacity=0.5, line_width=0)
    figure.add_shape(type="rect", xref="paper", yref="y2",
                  x0=0, y0=00, x1=1, y1=30,
                  fillcolor="lightgreen", opacity=0.5, line_width=0)
    # Ajout des lignes de borne haute et basse
    figure.add_shape(type="line", xref="paper", yref="y2",
                  x0=0, y0=70, x1=1, y1=70,
                  line=dict(color="black", width=2))
    figure.add_shape(type="line", xref="paper", yref="y2",
                  x0=0, y0=30, x1=1, y1=30,
                  line=dict(color="black", width=2))

    return figure, dftmp.index[-1]

# Fonction pour calculer le RSI
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100./(1.+rs)

    for i in range(period, len(prices)):
        delta = deltas[i-1]

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    # Retourner une série pandas avec le bon index
    return pd.Series(rsi, index=prices.index)
