from dash import callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from trade.defaults import defaults as dlt
from trade.locales import translations as tls


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
    Output("input-steps-per-candle", "value"),
    Output("input-initial-bars", "value"),

    Input('settings-tabs', 'value'),

    Input("update-time", "data"),
    Input("max-requests", "data"),
    Input("initial-cashflow", "data"),
    Input("simulation-duration", "data"),
    Input("news-font-size", "data"),
    Input("steps-per-candle", "data"),
    Input("initial-bars", "data"),
)
def set_advanced_settings_default_values(tabs, update_time, max_requests, init_cashflow, simulation_duration, news_font_size, steps_per_candle, initial_bars):
    """
    Default values for the advanced settings inputs
    (PS : settings-tabs is used to refresh the callback when the tab is switched)
    """
    steps = str(steps_per_candle if steps_per_candle is not None else dlt.steps_per_candle)
    bars = initial_bars if initial_bars is not None else dlt.initial_reveal_bars
    return update_time, max_requests, init_cashflow, simulation_duration, news_font_size, steps, bars


@callback(
    Output("update-time", "data"),
    Output("max-requests", "data"),
    Output("initial-cashflow", "data"),
    Output("simulation-duration", "data"),
    Output("news-font-size", "data"),
    Output("steps-per-candle", "data"),
    Output("initial-bars", "data"),
    Output("notifications", "children", allow_duplicate=True),

    Input("update-advanced-settings", "n_clicks"),

    State("input-update-time", "value"),
    State("input-max-requests", "value"),
    State("input-init-cashflow", "value"),
    State("input-simulation-duration", "value"),
    State("input-news-font-size", "value"),
    State("input-steps-per-candle", "value"),
    State("input-initial-bars", "value"),
    State("url", "search"),
    prevent_initial_call=True
)
def update_advanced_settings(n, update_time, max_requests, init_cashflow, simulation_duration, news_font_size, steps_per_candle, initial_bars, search):
    """Update the advanced settings stores with inputs values when the button is clicked"""

    if n is None or n == 0:
        raise PreventUpdate

    lang = "en" if (search and "lang=en" in search) else "fr"
    tl = tls[lang]["settings"]["advanced"]["notif"]

    if update_time is None or max_requests is None or init_cashflow is None or simulation_duration is None or news_font_size is None or steps_per_candle is None or initial_bars is None:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, dmc.Notification(
            title=tl["error-title"],
            id="simple-notify",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message=tl["error-message"],
        )

    else:
        return update_time, max_requests, init_cashflow, simulation_duration, news_font_size, int(steps_per_candle), int(initial_bars), dmc.Notification(
            id="notification-settings-updated",
            title=tl["success-title"],
            action="show",
            color="green",
            message=tl["success-message"],
        )
