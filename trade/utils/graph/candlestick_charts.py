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
            # And so with the same timestamp as the previous graph.
            # Never trim: show every candle revealed so far.
            dftmp = dataframe.iloc[: idx]

    # Strip rows where OHLC data is absent (tickers with fewer data points than
    # the shared index length produce NaN-padded trailing rows; rendering those
    # causes 0-height phantom candles and frozen MA lines).
    plot_df = dftmp.dropna(subset=['Open', 'High', 'Low', 'Close'])

    if plot_df.empty:
        # Window has moved entirely past this ticker's data — return a blank
        # figure but still advance the timestamp so the simulation clock keeps
        # running and other tickers remain unaffected.
        return go.Figure(), dftmp.index[-1]

    # Fixed horizontal slots: candle i always sits in slot i of the TOTAL
    # candle count of the file (not the number shown so far). A category axis
    # ordered by `all_labels` gives exactly that, since slot position is the
    # candle's position in the full list. The same string labels are used for
    # every trace so they line up with the slots.
    all_labels = [str(i) for i in dataframe.dropna(subset=['Open', 'High', 'Low', 'Close']).index]
    x_labels = [str(i) for i in plot_df.index]

    # creating the plot the short moving average
    short_mov_av = go.Scatter(
        x=x_labels,
        y=plot_df['short_MA'],
        name='shortMA'
    )

    # creating the plot the long moving average
    long_mov_av = go.Scatter(
        x=x_labels,
        y=plot_df['long_MA'],
        name='longMA'
    )

    # creating the plot the 200 moving average
    twohun_mov_av = go.Scatter(
        x=x_labels,
        y=plot_df['200_MA'],
        name='twohunMA'
    )

    # creating the plot the candlestick plot
    candelstick = go.Candlestick(
        x=x_labels,
        open=plot_df['Open'],
        high=plot_df['High'],
        low=plot_df['Low'],
        close=plot_df['Close'],
        name='price',
        showlegend=False
    )

    # Create chart for the selected stock
    figure = go.Figure(data=[long_mov_av, short_mov_av, twohun_mov_av, candelstick])

    # Category axis in full-file order: slot i is candle i. Ticks are limited to
    # dates already shown so future dates aren't revealed on the axis.
    # Few, horizontal labels keep the axis short so the candles get the height.
    # Ticks sit at evenly spaced slots across the WHOLE file width (about 6 in
    # total), so they stay far apart and never move as candles are added. Only
    # the ones already revealed are drawn. plot_df is a prefix of the full
    # data, so slot i in all_labels is also candle i of x_labels.
    tick_step = max(1, len(all_labels) // 6)
    tick_labels = all_labels[:len(x_labels):tick_step]
    figure.update_xaxes(
        type='category',
        categoryorder='array',
        categoryarray=all_labels,
        tickmode='array',
        tickvals=tick_labels,
        ticktext=[label[:10] for label in tick_labels],
        tickangle=0,
    )

    # Price axis on the right, with a dashed line + label at the latest close.
    figure.update_yaxes(side='right')
    last_close = float(plot_df['Close'].iloc[-1])
    figure.add_hline(
        y=last_close,
        line_dash='dash',
        line_width=1,
        line_color='gray',
        annotation_text=f'€{last_close:,.2f}',
        # Inside the plot, as a filled tag, so it doesn't print over the
        # right-hand axis numbers.
        annotation_position='top right',
        annotation_bgcolor='gray',
        annotation_font_color='white',
        annotation_font_size=11,
    )

    # While following the live edge, every frame shows ALL slots (the chart
    # fills left to right and never scrolls) and rescales the price axis to the
    # highest High / lowest Low shown so far plus 15% padding. Skipped while
    # `follow` is False so a user's manual pan/zoom isn't overridden.
    if follow:
        figure.update_xaxes(range=[-0.5, len(all_labels) - 0.5])
        hi = float(plot_df['High'].max())
        lo = float(plot_df['Low'].min())
        pad = (hi - lo) * 0.15 or hi * 0.01
        figure.update_yaxes(range=[lo - pad, hi + pad])

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
