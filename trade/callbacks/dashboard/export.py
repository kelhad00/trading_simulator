from dash import Output, Input, State, callback, no_update, ALL, ctx
from dash.exceptions import PreventUpdate
from trade.utils.export import export_data, new_session_id
from trade.utils.candle_steps import market_time


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
    State("max-requests", "data"),
    State('candle-step', 'data'),
    State('steps-per-candle', 'data'),
    State('session-id', 'data'),
    prevent_initial_call=True

)
def export_display_update(company, title, graph_segmented, request_segmented, requests, delete_requests, delete_all_requests, cashflow, timestamp, shares, totals, max_requests,
                           candle_step, steps_per_candle, session_id=None):
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

    # Moving candles: log the minute reached inside the candle (e.g. 00:15), not just the day
    export_data(market_time(timestamp, candle_step, steps_per_candle), requests, cashflow, shares, totals, company, title, graph_segmented, request_segmented, delete, max_requests=max_requests, session_id=session_id)
    return no_update


@callback(
    Output('session-id', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    State('session-id', 'data'),
    prevent_initial_call='initial_duplicate',
)
def give_tab_a_session_id(pathname, session_id):
    """Opening the dashboard without a session ID starts a new session: its logs
    get their own folder (data/exports/<session id>/). A refresh keeps the ID."""
    if session_id or not (pathname or "").startswith("/dashboard"):
        raise PreventUpdate
    return new_session_id()
