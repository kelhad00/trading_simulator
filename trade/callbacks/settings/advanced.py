import os.path
import pandas as pd

from dash import callback, Input, Output, State, ALL, no_update, dcc, page_registry
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from trade.utils.ordinal import ordinal
from trade.utils.settings.create_market_data import bull_trend, bear_trend, flat_trend, export_generated_data, \
    get_generated_data
from trade.utils.settings.display import display_chart
from trade.utils.settings.data_handler import scale_market_data, load_data, get_data_size
from trade.layouts.settings.sections.charts import timeline_item
from trade.defaults import defaults as dlt
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
def update_advanced_settings_values(tabs, update_time, max_requests, init_cashflow):
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
    if n is None or n == 0:
        raise PreventUpdate

    if update_time is None or max_requests is None or init_cashflow is None:
        return no_update, no_update, no_update, dmc.Notification(
            title="Error",
            id="simple-notify",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message="Please fill all the fields",
        )

    return update_time, max_requests, init_cashflow, dmc.Notification(
            id="notification-company-added",
            title="Company added",
            action="show",
            color="green",
            message=f"Settings updated !",
        )
