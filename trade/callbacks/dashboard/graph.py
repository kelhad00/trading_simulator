from dash import Output, Input, State, callback, page_registry, ctx
import plotly.graph_objects as go

import pandas as pd
import os

from trade.utils.graph.candlestick_charts import create_graph
from trade.utils.market import get_market_dataframe
from trade.locales import translations as tls
from trade.defaults import defaults as dlt


@callback(
    Output("periodic-updater", "interval"),
    Input("update-time", "data"),
)
def update_interval(update_time):
    """Function to update the interval of the periodic updater"""
    return int(update_time)


@callback(
    Output("timer", "children"),
    Input("timestamp", "data"),
)
def cb_update_timestamp(timestamp):
    """Function to update the timestamp displayed on the page"""
    timestamp = pd.to_datetime(timestamp)
    return timestamp.strftime("%Y-%m-%d")


@callback(
    Output('timestamp', 'data'),
    Output('company-graph', 'figure'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data')
)
def update_graph(n, company, timestamp, range=100):
    """
    Function to update the market graph with the latest data and timestamp
    Args:
        company: The selected company
        timestamp: The last timestamp
    Returns:
        The updated timestamp and the new graph
    """

    # Determining which callback input changed
    if ctx.triggered_id == 'periodic-updater':
        next_graph = True
    else:
        next_graph = False  # Don't update the timestamp if the user selects a new company

    dftmp = get_market_dataframe()[company]

    fig, timestamp = create_graph(
        dftmp,
        timestamp,
        next_graph,
        range
    )

    # Define chart layouts
    fig.update_layout(
        xaxis_title=tls[page_registry['lang']]["market-graph"]['x'],
        yaxis_title=tls[page_registry['lang']]["market-graph"]['y'],
        yaxis_tickprefix='€',
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(x=0, y=1.0),
        xaxis_rangeslider_visible=False,
    )

    # Change language on the legend
    fig.for_each_trace(
        lambda t: t.update(name=tls[page_registry["lang"]]["market-graph"]['legend'][t.name])
    )

    return timestamp, fig

@callback(
    Output('revenue-graph', 'figure'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data')
)
def update_revenue(n, company, timestamp):
    # If the user select an index, force the tab to be the market graph
    # if company in dlt.indexes.keys():
    #     return no_update

    timestamp = pd.to_datetime(timestamp)

    # When it's the timestamp that calls the callback,
    # it's possible that a new year is available, so update the information.
    # Otherwise, nothing is done.
    # We therefore only check if an additional year is available,
    # if the current timestamp is the first week of the year.
    # if ctx.triggered_id == 'market-timestamp-value' and timestamp.week > 1:
    # 	raise PreventUpdate
    # Using this method prevents income from being displayed
    # for as long as the user has not changed company,
    # unless it's the first week of the year.
    # TODO: So we need to find another way of optimizing

    # Import income data of the selected company
    file_path = os.path.join(dlt.data_path, 'revenue.csv')
    df = pd.read_csv(file_path, index_col=0, header=[0, 1])

    # Format these data to be easily used
    df = df[company].T.reset_index()
    df['asOfDate'] = pd.to_datetime(df['asOfDate']).dt.year
    df['NetIncome'] = pd.to_numeric(df['NetIncome'], errors='coerce')
    df['TotalRevenue'] = pd.to_numeric(df['TotalRevenue'], errors='coerce')

    # Filter the data to only keep the data from the previous years
    year = timestamp.year
    df = df.loc[df['asOfDate'] < year]

    # Create the graph
    fig = go.Figure(data=[
        go.Bar(
            name=tls[page_registry["lang"]]["revenue-graph"]['totalRevenue'],
            x=df['asOfDate'], y=df['TotalRevenue']
        ),
        go.Bar(
            name=tls[page_registry["lang"]]["revenue-graph"]['netIncome'],
            x=df['asOfDate'], y=df['NetIncome']
        )
    ])
    fig.update_layout(
        yaxis_tickprefix='€',
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(x=0, y=1.0)
    )

    if ctx.triggered_id == 'company-selector':
        # Go back to the market graph when the user selects a new company
        return fig
    else:
        # If new information has been added, add it to the revenue graph,
        # but don't change anything else.
        return fig


@callback(
    Output('revenue-graph', 'style'),
    Output('company-graph', 'style'),
    Input('segmented', "value")
)
def toggle_graph_type(value):
    """
    Function to toggle between the market graph and the revenue graph
    Args:
        value: The value of the segmented control
    Returns:
        The style of the revenue graph and the market graph
    """
    lang = page_registry['lang']

    if value == tls[lang]['tab-market']:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'none'}


