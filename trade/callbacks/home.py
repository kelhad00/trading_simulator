import os

from dash import callback, Input, Output, State, no_update
import dash_mantine_components as dmc

from trade.defaults import defaults as dlt
from trade.locales import translations as tls

APP_MODE = os.getenv('APP_MODE', 'config')


def _files_ok():
    return (
        os.path.exists(os.path.join(dlt.data_path, "generated_data.csv"))
        and os.path.exists(os.path.join(dlt.data_path, "news.csv"))
    )


def _missing_labels(companies):
    """Return list of tickers that have got_charts=True but an empty label."""
    if not companies:
        return []
    return [
        ticker
        for ticker, info in companies.items()
        if info.get("got_charts") and not (info.get("label") or "").strip()
    ]


_LINK_STYLE_BASE = {"textDecoration": "none", "display": "block"}

if APP_MODE == 'config':
    @callback(
        Output("export-session-btn", "disabled"),
        Output("export-tooltip", "disabled"),
        Input("url", "pathname"),
        Input("companies", "data"),
    )
    def update_export_button(pathname, companies):
        files_ok = _files_ok()
        return not files_ok, files_ok  # tooltip hidden once data exists


if APP_MODE == 'runtime':
    @callback(
        Output("start-simulation-btn", "disabled"),
        Output("start-simulation-btn-link", "style"),
        Output("start-tooltip", "disabled"),
        Input("imported-session-name", "data"),
        prevent_initial_call=False,
    )
    def update_start_button(imported_session_name):
        is_disabled = not imported_session_name
        link_style = {**_LINK_STYLE_BASE, "pointerEvents": "none" if is_disabled else "auto"}
        return is_disabled, link_style, not is_disabled  # tooltip hidden once session imported


@callback(
    Output("notifications", "children", allow_duplicate=True),
    Input("companies", "data"),
    Input("url", "pathname"),
    State("url", "search"),
    prevent_initial_call=True,
)
def notify_missing_labels(companies, pathname, search):
    """
    Show a warning notification when active companies have empty labels.
    Only fires after the first render (prevent_initial_call=True) so it
    doesn't spam on every page load — only when something changes.
    """
    if not _files_ok():
        return no_update

    missing = _missing_labels(companies)
    if not missing:
        return no_update

    lang = "en" if (search and "lang=en" in search) else "fr"
    tl = tls[lang]["settings"]["tickers"]["validation"]

    return dmc.Notification(
        id="notif-missing-label",
        title=tl["missing-label-title"],
        message=tl["missing-label-msg"],
        color="yellow",
        action="show",
        autoClose=5000,
    )
