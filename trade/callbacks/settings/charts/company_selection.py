from dash import callback, Input, Output, State
from dash.exceptions import PreventUpdate


@callback(
    Output("select-companies-charts", "data"),
    Input("settings-tabs", "value"),
    Input("companies", "data"),
)
def update_companies_multiselect(_tabs, companies):
    if not companies:
        return []
    # Show ticker only as label/value
    return [{"label": ticker, "value": ticker} for ticker in companies.keys()]


@callback(
    Output("select-companies-charts", "value", allow_duplicate=True),
    Input("select-all-companies-charts", "n_clicks"),
    State("companies", "data"),
    prevent_initial_call=True,
)
def select_all_companies_charts(n_clicks, companies):
    if not n_clicks:
        raise PreventUpdate
    return list(companies.keys()) if companies else []


@callback(
    Output("select-companies-charts", "value", allow_duplicate=True),
    Input("select-unconfigured-companies-charts", "n_clicks"),
    State("companies", "data"),
    State("company-configs", "data"),
    prevent_initial_call=True,
)
def select_unconfigured_companies_charts(n_clicks, companies, company_configs):
    if not n_clicks:
        raise PreventUpdate
    if not companies:
        return []
    company_configs = company_configs or {}
    # Not configured if no saved config exists yet
    return [ticker for ticker in companies.keys() if ticker not in company_configs] 