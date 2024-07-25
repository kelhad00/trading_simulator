from dash import callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_mantine_components as dmc


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

    if update_time is None or max_requests is None or init_cashflow is None:  # Check if all the fields are filled
        return no_update, no_update, no_update, dmc.Notification(
            title="Error",
            id="simple-notify",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message="Please fill all the fields",
        )

    else:
        return update_time, max_requests, init_cashflow, dmc.Notification(
            id="notification-company-added",
            title="Company added",
            action="show",
            color="green",
            message="Settings updated !",
        )
