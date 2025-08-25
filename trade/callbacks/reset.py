import os
import pandas as pd

from dash import Output, Input, State, callback, page_registry, ctx, no_update
from dash.exceptions import PreventUpdate
from trade.utils.config import save_current_config

from trade.defaults import defaults as dlt
from trade.utils.market import get_first_timestamp, get_market_dataframe, format_timestamp
from trade.utils.news import get_news_dataframe
from trade.utils.settings.create_market_data import get_generated_data

market_df = get_market_dataframe()


@callback(
    Output("settings-button", "disabled"),
    Input("timestamp", "data"),
)
def disable_button(timestamp):
    """Enable or disable the settings button depending on the current timestamp.

    Args:
        timestamp: Current timestamp stored in the app state.

    Returns:
        bool: False to enable when at the first available timestamp, True otherwise.
    """
    timestamp = pd.to_datetime(timestamp)
    timestamp = format_timestamp(timestamp)
    first_timestamp = get_first_timestamp(market_df, 100)
    first_timestamp = pd.to_datetime(first_timestamp)
    first_timestamp = format_timestamp(first_timestamp)
    if timestamp == first_timestamp:
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
    """Reset all simulation stores and archive current export files.

    Args:
        btn: Number of clicks on the reset button.
        initial_cashflow (float): Initial cash available for the portfolio.
        nb_export (int): Current export session counter.

    Returns:
        tuple: (
            timestamp (str),
            cashflow (float),
            requests (list),
            portfolio_shares (dict[str, int]),
            portfolio_totals (dict[str, float]),
            nb_export (int)
        )
    """

    if btn is None or btn == 0:
        raise PreventUpdate

    # Sauvegarder la configuration actuelle
    save_current_config()

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
        src = os.path.join(content_path, file)
        dst = os.path.join(session_path, file)
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(src, dst)

    nb_export = len(os.listdir(os.path.join(dlt.data_path, "exports")))-1

    return timestamp, cashflow, requests, portfolio_value, portfolio_value, nb_export



@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('portfolio-totals', 'data', allow_duplicate=True),
    Output('nb_export', 'data', allow_duplicate=True),
    Input('reset-button-1', 'n_clicks'),
    State('initial-cashflow', 'data'),
    State("nb_export", "data"),

    prevent_initial_call=True,
)
def reset_modal(btn, initial_cashflow, nb_export):
    """Proxy for `reset_data` when reset originates from the modal.

    Args:
        btn: Number of clicks on the modal reset button.
        initial_cashflow (float): Initial cash available.
        nb_export (int): Current export session counter.

    Returns:
        Same values as returned by `reset_data`.
    """
    return reset_data(btn, initial_cashflow, nb_export)