import plotly.graph_objects as go
import pandas as pd
import time

from trade.defaults import defaults as dlt

PLOTLY_CONFIG = {
    'displaylogo': False,
    'modeBarButtonsToRemove': ['toImage', 'select', 'lasso2d'],
    'modeBarButtonsToAdd': ['drawline'],
}


MAX_DATE_LABELS = 8
_LABEL_STEPS = (1, 2, 5, 7, 14, 30, 60, 90, 180, 365)   # candles between two date labels


def _date_label_step(candles_on_screen):
    """Smallest round spacing that keeps at most MAX_DATE_LABELS dates on screen."""
    for step in _LABEL_STEPS:
        if candles_on_screen / step <= MAX_DATE_LABELS:
            return step
    return -(-candles_on_screen // MAX_DATE_LABELS)


def _slots_in_view(view_range, all_labels):
    """(first, last) candle slot on screen: the zoomed range, or the whole session."""
    last_slot = len(all_labels) - 1
    if not view_range:
        return 0, last_slot
    ends = []
    for end in view_range[:2]:
        try:
            ends.append(float(end))                       # slot numbers (category axis)
        except (TypeError, ValueError):
            ends.append(float(all_labels.index(str(end))) if str(end) in all_labels else None)
    if None in ends:
        return 0, last_slot
    first = max(0, int(-(-min(ends) // 1)))               # first whole slot inside the view
    last = min(last_slot, int(max(ends) // 1))
    return (first, last) if first <= last else (0, last_slot)


def create_graph(dataframe, timestamp='', next_graph=True, range=10, follow=True, partial=None, view_range=None):
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

    partial : callable, optional
        Moving candles: called with the newest timestamp shown, returns that
        candle's (open, high, low, close) at the current step, or None when
        it is closed. See trade/utils/candle_steps.py.

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

    # Moving candles: draw the newest candle as it looks at the current step,
    # and stop the moving averages at the last closed candle so they don't give
    # away where this one will close. Only when that candle is the newest row
    # (a ticker whose data already ended has nothing forming).
    if partial is not None and plot_df.index[-1] == dftmp.index[-1]:
        values = partial(plot_df.index[-1])
        if values is not None:
            plot_df = plot_df.copy()
            last = plot_df.index[-1]
            plot_df.loc[last, ['Open', 'High', 'Low', 'Close']] = values
            ma_cols = [col for col in ('short_MA', 'long_MA', '200_MA') if col in plot_df.columns]
            plot_df.loc[last, ma_cols] = float('nan')

    # Fixed horizontal slots: candle i always sits in slot i of the TOTAL
    # candle count of the file (not the number shown so far). A category axis
    # ordered by `all_labels` gives exactly that, since slot position is the
    # candle's position in the full list. The same string labels are used for
    # every trace so they line up with the slots.
    all_labels = [str(i) for i in dataframe.dropna(subset=['Open', 'High', 'Low', 'Close']).index]
    x_labels = [str(i) for i in plot_df.index]

    # Moving averages: always plain lines. Without mode='lines', Plotly adds a
    # marker on every point while a line has fewer than 20 points, so the
    # markers showed at the start of a session and vanished at candle 20.

    # creating the plot the short moving average
    short_mov_av = go.Scatter(
        x=x_labels,
        y=plot_df['short_MA'],
        name='shortMA',
        mode='lines',
    )

    # creating the plot the long moving average
    long_mov_av = go.Scatter(
        x=x_labels,
        y=plot_df['long_MA'],
        name='longMA',
        mode='lines',
    )

    # creating the plot the 200 moving average
    twohun_mov_av = go.Scatter(
        x=x_labels,
        y=plot_df['200_MA'],
        name='twohunMA',
        mode='lines',
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

    # Category axis in full-file order: slot i is candle i. Date labels:
    # - about 8 at most across what is on screen: the whole session normally,
    #   or the zoomed part (view_range), so a zoom on a few candles still
    #   shows several dates;
    # - at round spacings (every 1, 2, 5, 7, 14, 30... candles) counted from
    #   the first candle, so they don't jump around as candles are added;
    # - only on candles already shown, so future dates aren't revealed.
    # plot_df is a prefix of the full data, so slot i in all_labels is also
    # candle i of x_labels.
    first, last = _slots_in_view(view_range, all_labels)
    tick_step = _date_label_step(last - first + 1)
    # (no range() here: this function has a parameter named `range`)
    tick_labels = [label for i, label in enumerate(all_labels[:len(x_labels)])
                   if i % tick_step == 0 and first <= i <= last]
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
