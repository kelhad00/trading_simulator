from dash import Output, Input, State, callback, page_registry, ctx, no_update
import plotly.graph_objects as go
import pandas as pd

from trade.utils.graph.candlestick_charts import create_graph
from trade.utils.market import get_market_dataframe, get_last_timestamp, get_revenues_dataframe
from trade.locales import translations as tls
from trade.defaults import defaults as dlt


@callback(
    Output("company-selector", "data"),
    Output("company-selector", "value"),
    Input("companies", "data"),
    State("company-selector", "data"),
)
def update_select_companies_options(companies, select_options):
    """
    Function to update the options of the company selector
    Args:
        companies: The list of companies --> it contains all the companies, even the ones that don't have charts assigned
        select_options: The current options of the company selector
    Returns:
        The new options of the company selector
        the value of the company selector
    """
    # Get the companies that are in the portfolio
    options = [{"label": value["label"], "value": key} for key, value in companies.items() if value["got_charts"]]

    if select_options == options:
        value = no_update
    else:
        value = list(companies.keys())[0]

    return options, value



@callback(
    Output("modal", "opened", allow_duplicate=True),
    Input("timestamp", "data"),
    prevent_initial_call=True
)
def update_modal(timestamp):
    """
    Function to update the modal when the timestamp changes
    Args:
        timestamp: The new timestamp
    Returns:
        The new state of the modal
    """
    if timestamp == get_last_timestamp(get_market_dataframe()):
        return True
    else:
        return False



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
    try:

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

    except Exception as e:
        print("Error", e)
        return no_update, no_update

@callback(
    Output('revenue-graph', 'figure'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data'),
    State("companies", "data")
)
def update_revenue(n, company, timestamp, companies):
    """
    Function to update the revenue graph with the latest data
    Args:
        company: The selected company
        timestamp: The last timestamp
    Returns:
        The new revenue graph
    """
    try:
        # If the company is an index, don't display the revenue graph
        if companies[company]['activity'] == "Indice":
            return no_update

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

        df = get_revenues_dataframe()

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
    except Exception as e:
        print("Error", e)
        return no_update


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


