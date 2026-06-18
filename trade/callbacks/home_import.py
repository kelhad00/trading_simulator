import base64

from dash import Input, Output, State, callback, clientside_callback, no_update
import dash_mantine_components as dmc

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.market import get_market_dataframe, get_first_timestamp
from trade.utils.session import extract_session_zip

_UPLOAD_VISIBLE = {"display": "block"}
_UPLOAD_HIDDEN  = {"display": "none"}
_LOADED_VISIBLE = {
    "display": "flex",
    "width": "100%",
    "padding": "10px 16px",
    "borderWidth": "1px",
    "borderStyle": "solid",
    "borderRadius": "6px",
    "borderColor": "#2f9e44",
    "backgroundColor": "#ebfbee",
    "fontSize": "14px",
    "color": "#2f9e44",
    "alignItems": "center",
    "justifyContent": "space-between",
    "gap": "8px",
}
_LOADED_HIDDEN = {"display": "none"}


@callback(
    Output("companies", "data", allow_duplicate=True),
    Output("initial-cashflow", "data", allow_duplicate=True),
    Output("max-requests", "data", allow_duplicate=True),
    Output("update-time", "data", allow_duplicate=True),
    Output("simulation-duration", "data", allow_duplicate=True),
    Output("timestamp", "data", allow_duplicate=True),
    Output("notifications", "children", allow_duplicate=True),
    Output("imported-session-name", "data"),
    Output("upload-session", "contents"),
    Input("upload-session", "contents"),
    State("upload-session", "filename"),
    State("url", "search"),
    prevent_initial_call=True,
)
def import_session(contents, filename, search):
    if not contents:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

    lang = "en" if (search and "lang=en" in search) else "fr"
    tl = tls[lang]["session"]

    try:
        _header, b64_data = contents.split(",", 1)
        zip_bytes = base64.b64decode(b64_data)
        stores = extract_session_zip(zip_bytes, dlt.data_path)
    except Exception:
        notif = dmc.Notification(
            id="notif-session-import",
            title=tl["import-label"],
            message=tl["import-error"],
            color="red",
            action="show",
            autoClose=6000,
        )
        # Reset contents so re-upload of the same file will fire again
        return no_update, no_update, no_update, no_update, no_update, no_update, notif, no_update, None

    # Reload market data from the freshly written CSV and get the correct start timestamp
    market_df = get_market_dataframe()
    timestamp = get_first_timestamp(market_df, 100)

    display_name = filename or "session.zip"
    notif = dmc.Notification(
        id="notif-session-import",
        title=tl["import-label"],
        message=tl["import-success"],
        color="green",
        action="show",
        autoClose=5000,
    )
    return (
        stores["companies"],
        stores["initial-cashflow"],
        stores["max-requests"],
        stores["update-time"],
        stores["simulation-duration"],
        timestamp,
        notif,
        display_name,
        None,   # reset upload-session.contents so re-upload always fires
    )


@callback(
    Output("session-upload-area", "style"),
    Output("session-loaded-area", "style"),
    Output("imported-filename", "children"),
    Input("imported-session-name", "data"),
)
def update_session_import_area(filename):
    if filename:
        return _UPLOAD_HIDDEN, _LOADED_VISIBLE, filename
    return _UPLOAD_VISIBLE, _LOADED_HIDDEN, ""


@callback(
    Output("imported-session-name", "data", allow_duplicate=True),
    Output("upload-session", "contents", allow_duplicate=True),
    Input("clear-session-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_imported_session(n_clicks):
    if not n_clicks:
        return no_update, no_update
    return None, None


# Reset the native file input element so re-uploading the same file always fires
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            var inp = document.querySelector('#upload-session input[type=file]');
            if (inp) inp.value = '';
        }
        return '';
    }
    """,
    Output("_upload-reset", "children"),
    Input("clear-session-btn", "n_clicks"),
    prevent_initial_call=True,
)
