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
    """Export dashboard state and interactions to disk.

    This callback reacts to various dashboard interactions (company selection,
    request deletions, visibility changes on the graph, etc.) and writes a
    consolidated snapshot using `export_data`. It does not update the UI
    directly and returns `no_update`.

    Args:
        company (str): Selected company ticker.
        title (str): Current description title.
        graph_segmented (str): Selected tab for the main graph.
        request_segmented (str): Selected tab for the requests view.
        requests (list): Current list of pending requests.
        delete_requests (list): Per-row delete button click counts.
        delete_all_requests (int): Click count for the clear-all button.
        restyle_data (dict|list): Plotly restyle data when traces visibility changes.
        cashflow (float): Current available cash.
        timestamp (str): Current market timestamp.
        shares (dict): Portfolio shares by symbol.
        totals (dict): Portfolio totals by symbol.
        max_requests (int): Maximum allowed number of requests.

    Returns:
        no_update: No UI change; side effects are handled by `export_data`.
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
