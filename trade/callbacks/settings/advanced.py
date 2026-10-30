from dash import callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.market import get_market_dataframe
from trade.utils.trials import parse_checkpoints, history_bars


# The dark mode switch and its saved value. Showing reads the saved value as a
# State (it isn't woken by it): if it were, showing and saving would wake each
# other in a circle, and Dash shows a "Circular Dependencies" error.
@callback(
    Output("color-enabled-input", "checked"),
    Input("settings-tabs", "value"),
    State("color-enabled", "data"),
)
def show_color_setting(tab, saved):
    return saved if saved is not None else True


@callback(
    Output("color-enabled", "data"),
    Input("color-enabled-input", "checked"),
    prevent_initial_call=True,
)
def save_color_setting(checked):
    return bool(checked) if checked is not None else True


# The leaderboard switch, same as the dark mode switch above (off by default)
@callback(
    Output("leaderboard-enabled-input", "checked"),
    Input("settings-tabs", "value"),
    State("leaderboard-enabled", "data"),
)
def show_leaderboard_setting(tab, saved):
    return bool(saved)


@callback(
    Output("leaderboard-enabled", "data"),
    Input("leaderboard-enabled-input", "checked"),
    prevent_initial_call=True,
)
def save_leaderboard_setting(checked):
    return bool(checked)


# The chart's Autoscale / Reset axes buttons, same as the switches above (off by default)
@callback(
    Output("chart-buttons-enabled-input", "checked"),
    Input("settings-tabs", "value"),
    State("chart-buttons-enabled", "data"),
)
def show_chart_buttons_setting(tab, saved):
    return bool(saved)


@callback(
    Output("chart-buttons-enabled", "data"),
    Input("chart-buttons-enabled-input", "checked"),
    prevent_initial_call=True,
)
def save_chart_buttons_setting(checked):
    return bool(checked)


# Moving candles: price path inside a forming candle, "simple" (default) or "random".
# Saved as soon as it is chosen, like the switches above.
@callback(
    Output("input-candle-path", "value"),
    Input("settings-tabs", "value"),
    State("candle-path", "data"),
)
def show_candle_path_setting(tab, saved):
    return saved if saved in ("simple", "random") else dlt.candle_path


@callback(
    Output("candle-path", "data"),
    Input("input-candle-path", "value"),
    prevent_initial_call=True,
)
def save_candle_path_setting(value):
    return value if value in ("simple", "random") else dlt.candle_path


@callback(
    Output("input-update-time", "value"),
    Output("input-max-requests", "value"),
    Output("input-init-cashflow", "value"),
    Output("input-simulation-duration", "value"),
    Output("input-news-font-size", "value"),
    Output("input-steps-per-candle", "value"),
    Output("input-initial-bars", "value"),
    Output("input-commission-fee", "value"),
    Output("discrete-enabled-input", "checked"),
    Output("input-discrete-checkpoints", "value"),
    Output("input-discrete-zoom", "value"),

    Input('settings-tabs', 'value'),

    Input("update-time", "data"),
    Input("max-requests", "data"),
    Input("initial-cashflow", "data"),
    Input("simulation-duration", "data"),
    Input("news-font-size", "data"),
    Input("steps-per-candle", "data"),
    Input("initial-bars", "data"),
    Input("commission-fee", "data"),
    Input("discrete-enabled", "data"),
    Input("discrete-checkpoints", "data"),
    Input("discrete-zoom-candles", "data"),
)
def set_advanced_settings_default_values(tabs, update_time, max_requests, init_cashflow, simulation_duration, news_font_size, steps_per_candle, initial_bars,
                                         commission_fee=None, discrete=False, checkpoints=None, zoom_candles=None):
    """
    Default values for the advanced settings inputs
    (PS : settings-tabs is used to refresh the callback when the tab is switched)
    """
    steps = str(steps_per_candle if steps_per_candle is not None else dlt.steps_per_candle)
    bars = initial_bars if initial_bars is not None else dlt.initial_reveal_bars
    fee = commission_fee if commission_fee is not None else dlt.commission_fee
    checkpoints_text = ", ".join(str(c) for c in (checkpoints or dlt.discrete_checkpoints))
    zoom = zoom_candles if zoom_candles is not None else dlt.discrete_zoom_candles
    return update_time, max_requests, init_cashflow, simulation_duration, news_font_size, steps, bars, fee, \
        bool(discrete), checkpoints_text, zoom


@callback(
    Output("update-time", "data"),
    Output("max-requests", "data"),
    Output("initial-cashflow", "data"),
    Output("simulation-duration", "data"),
    Output("news-font-size", "data"),
    Output("steps-per-candle", "data"),
    Output("initial-bars", "data"),
    Output("commission-fee", "data"),
    Output("discrete-enabled", "data"),
    Output("discrete-checkpoints", "data"),
    Output("discrete-zoom-candles", "data"),
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
    State("input-commission-fee", "value"),
    State("discrete-enabled-input", "checked"),
    State("input-discrete-checkpoints", "value"),
    State("input-discrete-zoom", "value"),
    prevent_initial_call=True
)
def update_advanced_settings(n, update_time, max_requests, init_cashflow, simulation_duration, news_font_size, steps_per_candle, initial_bars, search,
                             commission_fee=dlt.commission_fee, discrete=False, checkpoints_text=None,
                             zoom_candles=dlt.discrete_zoom_candles):
    """Update the advanced settings stores with inputs values when the button is clicked"""

    if n is None or n == 0:
        raise PreventUpdate

    lang = "en" if (search and "lang=en" in search) else "fr"
    tl = tls[lang]["settings"]["advanced"]["notif"]

    def error(message):
        return (no_update,) * 11 + (dmc.Notification(
            title=tl["error-title"],
            id="simple-notify",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message=message,
        ),)

    fee_ok = commission_fee is not None and 0 <= float(commission_fee) <= dlt.max_commission_fee
    if update_time is None or max_requests is None or init_cashflow is None or simulation_duration is None or news_font_size is None or steps_per_candle is None or initial_bars is None \
            or not fee_ok or (zoom_candles is not None and float(zoom_candles) < 0):
        return error(tl["error-message"])
    zoom_candles = int(zoom_candles) if zoom_candles is not None else dlt.discrete_zoom_candles

    # Discrete mode: a valid candle list, and the session opens on the first trial
    checkpoints = no_update
    if discrete:
        market_df = get_market_dataframe()
        n_candles = len(market_df.index) if market_df is not None else 0
        checkpoints = parse_checkpoints(checkpoints_text, n_candles)
        if checkpoints is None:
            return error(tl["discrete-error"].format(n=n_candles))
        initial_bars = history_bars(checkpoints)

    return update_time, max_requests, init_cashflow, simulation_duration, news_font_size, int(steps_per_candle), int(initial_bars), float(commission_fee), \
        bool(discrete), checkpoints, zoom_candles, dmc.Notification(
            id="notification-settings-updated",
            title=tl["success-title"],
            action="show",
            color="green",
            message=tl["success-message"],
        )
