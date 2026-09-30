import time

import dash_mantine_components as dmc
from dash import Output, Input, State, callback, page_registry
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.locales import translations as tls

# Message text is in locales: notifications -> "reminder-<key>"
_REMINDERS = [
    (lambda e, d: e / d >= 0.25, '25pct', 'blue'),
    (lambda e, d: e / d >= 0.50, '50pct', 'blue'),
    (lambda e, d: e / d >= 0.75, '75pct', 'orange'),
    (lambda e, d: d - e <= 300,  '5min',  'orange'),
    (lambda e, d: d - e <= 120,  '2min',  'orange'),
    (lambda e, d: d - e <= 60,   '1min',  'red'),
]


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Output('shown-reminders', 'data'),
    Input('periodic-updater', 'n_intervals'),
    Input('timestamp', 'data'),
    State('session-start-time', 'data'),
    State('simulation-duration', 'data'),
    State('total-paused-seconds', 'data'),
    State('shown-reminders', 'data'),
    prevent_initial_call=True,
)
def fire_time_reminders(n, timestamp, session_start, sim_duration, total_paused, shown):
    if session_start is None:
        raise PreventUpdate

    elapsed = time.time() - session_start - (total_paused or 0)
    duration_secs = (sim_duration or dlt.simulation_duration) * 60
    shown = list(shown or [])

    tl = tls[page_registry.get('lang', 'fr')]["notifications"]
    new_notifications = []
    for condition, key, color in _REMINDERS:
        if key not in shown and condition(elapsed, duration_secs):
            shown.append(key)
            new_notifications.append(
                dmc.Notification(
                    id=f"reminder-{key}",
                    title=tl["simulation"],
                    message=tl[f"reminder-{key}"],
                    color=color,
                    action="show",
                    autoClose=6000,
                    icon=DashIconify(icon="material-symbols:timer", width=20),
                )
            )

    if not new_notifications:
        raise PreventUpdate

    return new_notifications, shown
