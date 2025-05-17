from dash import callback, Input, Output, State, no_update, page_registry
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from trade.locales import translations as tls


@callback(
Output("input-update-time", "value"),
    Output("input-max-requests", "value"),
    Output("input-init-cashflow", "value"),

    Input('settings-tabs', 'value'),

    Input("update-time", "data"),
    Input("max-requests", "data"),
    Input("initial-cashflow", "data"),
)
def set_advanced_settings_default_values(tabs, update_time, max_requests, init_cashflow):
    """
    Default values for the advanced settings inputs
    (PS : settings-tabs is used to refresh the callback when the tab is switched)
    """
    return update_time, max_requests, init_cashflow


@callback(
    Output("update-time", "data"),
    Output("max-requests", "data"),
    Output("initial-cashflow", "data"),
    Output("notifications", "children", allow_duplicate=True),

    Input("update-advanced-settings", "n_clicks"),

    State("input-update-time", "value"),
    State("input-max-requests", "value"),
    State("input-init-cashflow", "value"),
    prevent_initial_call=True
)
def update_advanced_settings(n, update_time, max_requests, init_cashflow):
    """Update the advanced settings stores with inputs values when the button is clicked"""

    if n is None or n == 0:
        raise PreventUpdate

    if update_time is None or not convertible_in_int(update_time) or max_requests is None or init_cashflow is None:  # Check if all the fields are filled
        return no_update, no_update, no_update, dmc.Notification(
            title=tls[page_registry["lang"]]["settings"]["advanced"]["notification"]["title_error"],
            id="simple-notify",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message=tls[page_registry["lang"]]["settings"]["advanced"]["notification"]["message_error"],
        )

    else:
        return update_time, max_requests, init_cashflow, dmc.Notification(
            id="simple-notify",
            title=tls[page_registry["lang"]]["settings"]["advanced"]["notification"]["title_update"],
            action="show",
            color="green",
            message=tls[page_registry["lang"]]["settings"]["advanced"]["notification"]["message_update"],
        )
def convertible_in_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False
