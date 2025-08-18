import json
import os
from dash import callback, Input, Output, State
from dash.exceptions import PreventUpdate


@callback(
    Output("company-configs", "data"),
    Input("settings-tabs", "value"),
)
def load_company_configs(_tab):
    # Start empty on page load; no persistence
    return {}


@callback(
    Output("company-configs", "data", allow_duplicate=True),
    Output('timeline', 'children', allow_duplicate=True),
    Output('select-companies-charts', 'value', allow_duplicate=True),
    Input("save-company-config", "n_clicks"),
    State("select-companies-charts", "value"),
    State("size-store", "data"),
    State("special-pattern-config", "data"),
    State("company-configs", "data"),
    prevent_initial_call=True,
)
def save_company_configs(n_clicks, selected_tickers, size_data, special_cfg, current_configs):
    if not n_clicks:
        raise PreventUpdate
    if not selected_tickers:
        raise PreventUpdate
    if not isinstance(current_configs, dict):
        current_configs = {}

    for ticker in selected_tickers:
        current_configs[ticker] = {
            "size_data": size_data or {},
            "special_pattern_config": special_cfg or {},
        }
    # No file persistence; stays in memory
    return current_configs, [], []


@callback(
    Output('refresh-button', 'disabled'),
    Input('company-configs', 'data'),
    Input('companies', 'data'),
)
def toggle_refresh_disabled(company_configs, companies):
    # Disable until all companies have a saved config
    if not companies:
        return True
    company_configs = company_configs or {}
    tickers = list(companies.keys())
    return not all(ticker in company_configs for ticker in tickers)


@callback(
    Output('save-company-config', 'disabled'),
    Input('timeline', 'children'),
)
def toggle_save_button_disabled(timeline_children):
    """Disable save button when timeline is empty"""
    if not timeline_children or len(timeline_children) == 0:
        return True
    return False 