import os
import threading

from dash import Output, Input, State, callback, page_registry, ctx, no_update
from dash.exceptions import PreventUpdate

from trade.defaults import defaults as dlt
from trade.utils.market import get_first_timestamp, get_market_dataframe
from trade.utils.news import get_news_dataframe
from trade.utils.settings.create_market_data import get_generated_data

market_df = get_market_dataframe()


def _archive_exports(nb_export):
    """Move export files to a numbered session folder in the background."""
    try:
        session_path = os.path.join(dlt.data_path, "exports", str(nb_export))
        os.makedirs(session_path, exist_ok=True)
        content_path = os.path.join(dlt.data_path, "export")
        for file in os.listdir(content_path):
            os.rename(
                os.path.join(content_path, file),
                os.path.join(session_path, file)
            )
    except Exception as e:
        print("Error archiving exports:", e)


_LINK_STYLE_BASE = {"textDecoration": "none", "display": "block"}

@callback(
    Output("settings-button", "disabled"),
    Output("settings-button-link", "style"),
    Input("_pages_location", "pathname"),
    Input("timestamp", "data"),
)
def disable_button(pathname, timestamp):
    if pathname != "/":
        raise PreventUpdate
    is_disabled = timestamp != get_first_timestamp(market_df, 100)
    return is_disabled, {**_LINK_STYLE_BASE, "pointerEvents": "none" if is_disabled else "auto"}


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
    if btn is None or btn == 0:
        raise PreventUpdate

    threading.Thread(target=_archive_exports, args=(nb_export,), daemon=True).start()

    timestamp = get_first_timestamp(market_df, 100)
    df = get_generated_data()
    companies = df.columns.get_level_values('symbol').unique() if df is not None else []
    portfolio_value = {c: 0 for c in companies}

    return timestamp, initial_cashflow, [], portfolio_value, portfolio_value, nb_export + 1


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
    return reset_data(btn, initial_cashflow, nb_export)