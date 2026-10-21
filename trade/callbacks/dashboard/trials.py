"""Discrete mode on the dashboard: the "Next trial" button (trade/utils/trials.py)."""
from dash import Output, Input, State, callback, no_update
from dash.exceptions import PreventUpdate

from trade.locales import translations as tls, language
from trade.utils.export import log_session_event
from trade.utils.logs import get_logger
from trade.utils.market import get_market_dataframe
from trade.utils.trials import candle_number, next_checkpoint, trial_position, walk_orders

logger = get_logger("trials")

_HIDDEN = {"display": "none"}


@callback(
    Output('next-trial-btn', 'style'),
    Output('next-trial-btn', 'children'),
    Input('timestamp', 'data'),
    Input('discrete-enabled', 'data'),
    State('discrete-checkpoints', 'data'),
    State("url", "search"),     # ?lang=en in this participant's address
)
def show_next_trial_button(timestamp, discrete, checkpoints, lang=None):
    """The button only exists in discrete mode; it says which trial is shown."""
    if not discrete or not checkpoints:
        return _HIDDEN, no_update
    t = tls[language(lang)]['trials']
    market_df = get_market_dataframe()
    number = candle_number(market_df.index, timestamp) if market_df is not None else None
    if number is None:
        raise PreventUpdate
    trial, total = trial_position(checkpoints, number)
    label = t['finish'] if next_checkpoint(checkpoints, number) is None else t['next']
    return {"display": "block"}, f"{label} ({trial}/{total})"


@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('cost-basis', 'data', allow_duplicate=True),
    Output('sold-data', 'data', allow_duplicate=True),
    Output('candle-step', 'data', allow_duplicate=True),
    # Tells update_graph to draw the new trial (after the timestamp has changed)
    Output('trial-jump', 'data'),
    Output('modal', 'opened', allow_duplicate=True),
    Output('periodic-updater', 'disabled', allow_duplicate=True),
    Input('next-trial-btn', 'n_clicks'),
    State('timestamp', 'data'),
    State('discrete-enabled', 'data'),
    State('discrete-checkpoints', 'data'),
    State('requests', 'data'),
    State('portfolio-shares', 'data'),
    State('cashflow', 'data'),
    State('cost-basis', 'data'),
    State('sold-data', 'data'),
    State('company-selector', 'value'),
    State('session-id', 'data'),
    prevent_initial_call=True,
)
def next_trial(n_clicks, timestamp, discrete, checkpoints, requests, port_shares, cashflow, cost_basis, sold_data,
               company=None, session_id=None):
    """Go to the next trial: check the waiting orders on every candle in between,
    then show the chart up to the next trial's candle. After the last trial the
    session ends (results window, as when the time is up)."""
    if not n_clicks or not discrete or not checkpoints:
        raise PreventUpdate
    market_df = get_market_dataframe()
    number = candle_number(market_df.index, timestamp) if market_df is not None else None
    if number is None:
        raise PreventUpdate

    target = next_checkpoint(checkpoints, number)
    if target is None:
        logger.info("Last trial done: session ended")
        log_session_event("session-finish", timestamp, cashflow, company, session_id)
        return (no_update,) * 8 + (True, True)

    requests = list(requests or [])
    cost_basis, sold_data = dict(cost_basis or {}), dict(sold_data or {})
    shares, cashflow = walk_orders(market_df, number, target, requests, dict(port_shares or {}), cashflow or 0,
                                   cost_basis, sold_data)
    new_ts = market_df.index[target - 1]
    log_session_event("next-trial", new_ts, cashflow, company, session_id)
    logger.info("Trial: candle %s -> %s", number, target)
    return new_ts, requests, shares, cashflow, cost_basis, sold_data, None, target, no_update, no_update
