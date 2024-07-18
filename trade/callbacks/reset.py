import os

from dash import Output, Input, State, callback, page_registry, ctx, no_update
from dash.exceptions import PreventUpdate

from trade.defaults import defaults as dlt
from trade.utils.market import get_first_timestamp, get_market_dataframe
from trade.utils.news import get_news_dataframe
from trade.utils.settings.create_market_data import get_generated_data

market_df = get_market_dataframe()


@callback(
    Output("settings-button", "disabled"),
    Input("timestamp", "data"),
)
def disable_button(timestamp):
    if timestamp == get_first_timestamp(market_df, 100):
        return False
    else:
        return True


@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('portfolio-totals', 'data', allow_duplicate=True),
    Output('nb_export', 'data'),
    Input('reset-button', 'n_clicks'),
    State('initial-cashflow', 'data'),
    State("nb_export", "data"),
    prevent_initial_call=True,
)
def reset_data(btn, initial_cashflow, nb_export):
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
    cashflow = initial_cashflow

    df = get_generated_data()  # Get the data of all companies
    companies = df.columns.get_level_values('symbol').unique()
    portfolio_value = {c: 0 for c in companies}

    requests = []

    # create dir named nb_export in data folder
    session_path = os.path.join(dlt.data_path, "exports", str(nb_export))
    os.makedirs(session_path, exist_ok=True)

    content_path = os.path.join(dlt.data_path, "export")

    # move all files from data/export to data/exports/nb_export
    for file in os.listdir(content_path):
        os.rename(os.path.join(content_path, file), os.path.join(session_path, file))

    nb_export = len(os.listdir(os.path.join(dlt.data_path, "exports")))

    return timestamp, cashflow, requests, portfolio_value, portfolio_value, nb_export



@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('portfolio-totals', 'data', allow_duplicate=True),
    Input('reset-button-1', 'n_clicks'),
    State('initial-cashflow', 'data'),
    State("nb_export", "data"),

    prevent_initial_call=True,
)
def reset_modal(btn, initial_cashflow, nb_export):
    return reset_data(btn, initial_cashflow, nb_export)