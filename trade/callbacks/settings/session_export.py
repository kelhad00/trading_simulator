import base64

from dash import Input, Output, State, callback

from trade.defaults import defaults as dlt
from trade.utils.session import build_session_zip


@callback(
    Output("download-session", "data"),
    Input("export-session-btn", "n_clicks"),
    State("companies", "data"),
    State("initial-cashflow", "data"),
    State("max-requests", "data"),
    State("update-time", "data"),
    State("simulation-duration", "data"),
    State("news-font-size", "data"),
    State("color-scheme-store", "data"),
    State("notif-enabled", "data"),
    prevent_initial_call=True,
)
def export_session(n_clicks, companies, initial_cashflow, max_requests, update_time, simulation_duration, news_font_size, color_scheme, notif_enabled):
    from dash import no_update
    if not n_clicks:
        return no_update
    zip_bytes = build_session_zip(
        companies=companies,
        initial_cashflow=initial_cashflow,
        max_requests=max_requests,
        update_time=update_time,
        simulation_duration=simulation_duration,
        news_font_size=news_font_size,
        color_scheme=color_scheme,
        notif_enabled=notif_enabled,
        data_path=dlt.data_path,
    )
    return {
        "content": base64.b64encode(zip_bytes).decode(),
        "filename": "session.zip",
        "base64": True,
        "type": "application/zip",
    }
