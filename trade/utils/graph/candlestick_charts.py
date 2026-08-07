import plotly.graph_objects as go
import pandas as pd
import time

from trade.defaults import defaults as dlt

PLOTLY_CONFIG = {
    'displaylogo': False,
    'modeBarButtonsToRemove': ['toImage', 'select', 'lasso2d'],
    'modeBarButtonsToAdd': ['drawline'],
}


def create_graph(dataframe, timestamp='', next_graph=True, range=10, follow=True):
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

    follow : bool
        whether the visible window should auto-scroll to keep showing the
        latest `range` candles (default: True). Set to False once the user
        has manually panned/zoomed away, so their view isn't pushed back to
        the live edge on the next update.

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
        idx = dataframe.index.get_loc(timestamp) + 1
        if idx == 1:  # if the timestamp is the first element of the dataframe
            if range == 0:
                dftmp = dataframe[:1]
            else:
                dftmp = dataframe[:range]
        elif next_graph:  # You want to see the graph with new data
            # Always keep the full history from the start so previously
            # rendered candles never disappear as new ones are added.
            dftmp = dataframe.iloc[:idx + 1]
        else:  # You want to see the graph of another company
            # And so with the same timestamp as the previous graph
            if range == 0 or idx < range:
                dftmp = dataframe.iloc[: idx]
            else:
                dftmp = dataframe.iloc[idx - range: idx]


    # Strip rows where OHLC data is absent (tickers with fewer data points than
    # the shared index length produce NaN-padded trailing rows; rendering those
    # causes 0-height phantom candles and frozen MA lines).
    plot_df = dftmp.dropna(subset=['Open', 'High', 'Low', 'Close'])

    if plot_df.empty:
        # Window has moved entirely past this ticker's data — return a blank
        # figure but still advance the timestamp so the simulation clock keeps
        # running and other tickers remain unaffected.
        return go.Figure(), dftmp.index[-1]

    # creating the plot the long moving average
    long_mov_av = go.Scatter(
        x=plot_df.index,
        y=plot_df['long_MA'],
        name='longMA'
    )

    # creating the plot the short moving average
    short_mov_av = go.Scatter(
        x=plot_df.index,
        y=plot_df['short_MA'],
        name='shortMA'
    )

    # creating the plot the 200 moving average
    twohun_mov_av = go.Scatter(
        x=plot_df.index,
        y=plot_df['200_MA'],
        name='twohunMA'
    )

    # creating the plot the candlestick plot
    candelstick = go.Candlestick(
        x=plot_df.index,
        open=plot_df['Open'],
        high=plot_df['High'],
        low=plot_df['Low'],
        close=plot_df['Close'],
        name='price',
        showlegend=False
    )

    # Create chart for the selected stock
    figure = go.Figure(data=[long_mov_av, short_mov_av, twohun_mov_av, candelstick])

    # The full history is always in the data now, but by default only show the
    # last `range` candles so the view keeps scrolling forward like before —
    # older candles shift out of view instead of being removed, and the user
    # can still pan/zoom back to see them. Skip this while `follow` is False
    # (user has manually panned away) so the update doesn't yank their view
    # back to the live edge.
    if follow and range:
        visible = plot_df.iloc[-range:] if 0 < range < len(plot_df) else plot_df
        # The index may be plain date strings (unparsed CSV column) rather than
        # a DatetimeIndex, so parse the endpoints before doing date arithmetic.
        start = pd.Timestamp(visible.index[0])
        end = pd.Timestamp(visible.index[-1])
        step = (end - start) / (len(visible) - 1) if len(visible) >= 2 else pd.Timedelta(days=1)
        # Leave a little breathing room (a few candle-widths) to the right of
        # the latest candle so it isn't flush against the edge of the plot.
        figure.update_xaxes(range=[start, end + step * 3])

    return figure, dftmp.index[-1]


if __name__ == '__main__':
    import os

    name = 'MC.PA'

    file_path = os.path.join(dlt.data_path, 'market_data.csv')
    df = pd.read_csv(file_path, header=[0, 1], index_col=0)[name]

    fig, endtime = create_graph(df)
    fig.show(config=PLOTLY_CONFIG)

    testtime = 3
    while testtime > 0:
        time.sleep(5)

        fig, endtime = create_graph(df, endtime)

        fig.show(config=PLOTLY_CONFIG)

        testtime -= 1
