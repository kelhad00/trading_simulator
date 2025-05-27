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
    Input('company-graph', 'restyleData'),

    State('cashflow', 'data'),
    State('timestamp', 'data'),
    State('portfolio-shares', 'data'),
    State("portfolio-totals", "data"),
    State("max-requests", "data"),
    prevent_initial_call=True

)
def export_display_update(company, title, graph_segmented, request_segmented, requests, delete_requests, delete_all_requests, restyle_data, cashflow, timestamp, shares, totals, max_requests):
    """
    Function triggered when the user interacts with the dashboard
    Update the logs with the latest data
    """
    if ctx.triggered_id == 'clear-done-btn':
        delete = ["all"]
    else:
        try:
            if ctx.triggered_id == 'company-graph':
                # Cas où l'utilisateur a modifié la visibilité des courbes
                delete = []
            else:
                index = ctx.triggered_id['index']
                if delete_requests[index] is not None:
                    delete = [index]
                else:
                    return no_update
        except:
            delete = []

    export_data(
        timestamp, 
        requests, 
        cashflow, 
        shares, 
        totals, 
        company, 
        title, 
        graph_segmented, 
        request_segmented, 
        delete, 
        trigger=ctx.triggered_id,
        restyle_data=restyle_data,
        max_requests=max_requests
    )
    return no_update
