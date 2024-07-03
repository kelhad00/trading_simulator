from dash import Output, Input, State, html, callback, no_update
from trade.utils.store.export import export_data


@callback(
    Output("export", "children"),

    Input("company-selector", "value"),
    Input('description-title', 'children'),
    Input('segmented', "value"),
    Input("action-input", "value"),

    State('cashflow', 'data'),
    State('timestamp', 'data'),
    State('portfolio-shares', 'data'),
    State("portfolio-totals", "data"),
    State("requests", "data"),
)
def export_display_update(company, title, graph_segmented, request_segmented, cashflow, timestamp, shares, totals, requests):
    """
    Function triggered when the user interacts with the dashboard
    Update the logs with the latest data
    """
    export_data(timestamp, requests, cashflow, shares, totals, company, title, graph_segmented, request_segmented)
    return no_update
