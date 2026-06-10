import base64

from dash import Input, Output, State, callback, no_update
import dash_mantine_components as dmc

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.session import extract_session_zip


@callback(
    Output("companies", "data", allow_duplicate=True),
    Output("initial-cashflow", "data", allow_duplicate=True),
    Output("max-requests", "data", allow_duplicate=True),
    Output("update-time", "data", allow_duplicate=True),
    Output("notifications", "children", allow_duplicate=True),
    Input("upload-session", "contents"),
    State("url", "search"),
    prevent_initial_call=True,
)
def import_session(contents, search):
    if not contents:
        return no_update, no_update, no_update, no_update, no_update

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
        return no_update, no_update, no_update, no_update, notif

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
        notif,
    )
