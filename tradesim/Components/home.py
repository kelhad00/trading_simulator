from dash import Output, Input, State, dcc
import dash
from dash.exceptions import PreventUpdate

@dash.callback(
    Output('home-start-button', 'style'),
    Output('home-start-button-info', 'style'),
    Input('home-clock', 'n_intervals'),
)
def manage_home_start_button(n):
    # Import here to prevent circular import
    from tradesim.app import app

    if app.home_start_button_disabled:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'inline'}, {'display': 'none'}


@dash.callback(
    Output('market-timestamp-value', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('request-list', 'data', allow_duplicate=True),
    Output('portfolio_shares', 'data', allow_duplicate=True),
    Output('portfolio_totals', 'data', allow_duplicate=True),
    Input('restart_sim', 'n_clicks'),
    prevent_initial_call=True,
)
def reset_data(btn):
    if btn is None:
        raise PreventUpdate
    
    # Import here to prevent circular import
    from tradesim.defaults import defaults as dlt

    # Reset the data of each dcc.Store component
    marketTimestampValue = ""
    cashflow = dlt.initial_money
    requestList = []
    portfolioShares = {c: {'Shares': 0} for c in dlt.companies.keys()}
    portfolioTotals = {c: {'Total': 0} for c in dlt.companies.keys()}

    return marketTimestampValue, cashflow, requestList, portfolioShares, portfolioTotals