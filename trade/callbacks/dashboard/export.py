from dash import Output, Input, State, callback, no_update, ALL
from trade.utils.export import export_data


@callback(
    Output("export", "children"),

    Input("company-selector", "value"),
    Input('description-title', 'children'),
    Input('segmented', "value"),
    Input("action-input", "value"),
    Input("requests", "data"),

    State('cashflow', 'data'),
    State('timestamp', 'data'),
    State('portfolio-shares', 'data'),
    State("portfolio-totals", "data"),
    State({'type': 'requests-selectable-table', 'index': ALL}, "checked"),

    prevent_initial_call=True

)
def export_display_update(company, title, graph_segmented, request_segmented, requests, cashflow, timestamp, shares, totals, deleted_request):
    """
    Function triggered when the user interacts with the dashboard
    Update the logs with the latest data
    """
    export_data(timestamp, requests, cashflow, shares, totals, company, title, graph_segmented, request_segmented, deleted_request)
    return no_update
