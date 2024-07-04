from dash import Output, Input, State, callback, page_registry, ctx, no_update
from dash.exceptions import PreventUpdate

from trade.defaults import defaults as dlt
from trade.utils.market import get_first_timestamp, get_market_dataframe
from trade.utils.news import get_news_dataframe

market_df = get_market_dataframe()


@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('portfolio-totals', 'data', allow_duplicate=True),
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True,
)
def reset_data(btn):
    """
    Function to reset the simulation data
    Args:
        btn: The reset button
    Returns:
        The initial data of the simulation
    """

    if btn is None or btn == 0:
        raise PreventUpdate

    # Reset the data of each dcc.Store component
    timestamp = get_first_timestamp(market_df, 100)
    cashflow = dlt.initial_money
    shares = {c: 0 for c in dlt.companies.keys()}
    totals = {c: 0 for c in dlt.companies.keys()}
    requests = []

    return timestamp, cashflow, requests, shares, totals