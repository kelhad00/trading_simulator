from dash import callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_mantine_components as dmc


@callback(
    Output("color-enabled-input", "checked"),
    Input("settings-tabs", "value"),
    Input("color-enabled", "data"),
)
def set_color_enabled_default(tabs, color_enabled):
    return color_enabled if color_enabled is not None else True


@callback(
    Output("color-enabled", "data"),
    Input("color-enabled-input", "checked"),
    prevent_initial_call=True,
)
def sync_color_enabled(enabled):
    return bool(enabled) if enabled is not None else True


@callback(
    Output("input-update-time", "value"),
    Output("input-max-requests", "value"),
    Output("input-init-cashflow", "value"),
    Output("input-simulation-duration", "value"),
    Output("input-news-font-size", "value"),

    Input('settings-tabs', 'value'),

    Input("update-time", "data"),
    Input("max-requests", "data"),
    Input("initial-cashflow", "data"),
    Input("simulation-duration", "data"),
    Input("news-font-size", "data"),
)
def set_advanced_settings_default_values(tabs, update_time, max_requests, init_cashflow, simulation_duration, news_font_size):
    """
    Default values for the advanced settings inputs
    (PS : settings-tabs is used to refresh the callback when the tab is switched)
    """
    return update_time, max_requests, init_cashflow, simulation_duration, news_font_size


@callback(
    Output("update-time", "data"),
    Output("max-requests", "data"),
    Output("initial-cashflow", "data"),
    Output("simulation-duration", "data"),
    Output("news-font-size", "data"),
    Output("notifications", "children", allow_duplicate=True),

    Input("update-advanced-settings", "n_clicks"),

    State("input-update-time", "value"),
    State("input-max-requests", "value"),
    State("input-init-cashflow", "value"),
    State("input-simulation-duration", "value"),
    State("input-news-font-size", "value"),
    prevent_initial_call=True
)
def update_advanced_settings(n, update_time, max_requests, init_cashflow, simulation_duration, news_font_size):
    """Update the advanced settings stores with inputs values when the button is clicked"""

    if n is None or n == 0:
        raise PreventUpdate

    if update_time is None or max_requests is None or init_cashflow is None or simulation_duration is None or news_font_size is None:
        return no_update, no_update, no_update, no_update, no_update, dmc.Notification(
            title="Error",
            id="simple-notify",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message="Please fill all the fields",
        )

    else:
        return update_time, max_requests, init_cashflow, simulation_duration, news_font_size, dmc.Notification(
            id="notification-company-added",
            title="Company added",
            action="show",
            color="green",
            message="Settings updated !",
        )
