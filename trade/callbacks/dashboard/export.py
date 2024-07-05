from dash import Output, Input, State, callback, no_update, ALL, ctx
from trade.utils.export import export_data


@callback(
    Output("export", "children"),

    Input("company-selector", "value"),
    Input('description-title', 'children'),
    Input('segmented', "value"),
    Input("action-input", "value"),
    Input("requests", "data"),
    Input({'type': 'requests-selectable-table', 'index': ALL}, "n_clicks"),
    Input('clear-done-btn', 'n_clicks'),

    State('cashflow', 'data'),
    State('timestamp', 'data'),
    State('portfolio-shares', 'data'),
    State("portfolio-totals", "data"),

    prevent_initial_call=True

)
def export_display_update(company, title, graph_segmented, request_segmented, requests, delete_requests, delete_all_requests, cashflow, timestamp, shares, totals):
    """
    Function triggered when the user interacts with the dashboard
    Update the logs with the latest data
    """
    if ctx.triggered_id == 'clear-done-btn':
        delete = ["all"]
    else:
        try:
            index = ctx.triggered_id['index']
            if delete_requests[index] is not None:
                delete = [index]
            else:
                return no_update
        except:
            delete = []

    print(ctx.triggered_id)





    export_data(timestamp, requests, cashflow, shares, totals, company, title, graph_segmented, request_segmented, delete)
    return no_update
