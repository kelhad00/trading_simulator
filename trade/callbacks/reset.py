import os
import threading

import dash_mantine_components as dmc
from dash import Output, Input, State, callback, clientside_callback, html, page_registry, ctx, no_update
from dash.exceptions import PreventUpdate

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.market import get_market_dataframe, get_start_timestamp
from trade.utils.news import get_news_dataframe
from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.logs import get_logger

logger = get_logger("reset")

APP_MODE = os.getenv('APP_MODE', 'config')


def _archive_exports(nb_export):
    """Move export files to a numbered session folder in the background."""
    try:
        session_path = os.path.join(dlt.data_path, "exports", str(nb_export))
        os.makedirs(session_path, exist_ok=True)
        content_path = os.path.join(dlt.data_path, "export")
        for file in os.listdir(content_path):
            os.rename(
                os.path.join(content_path, file),
                os.path.join(session_path, file)
            )
    except Exception as e:
        logger.error("Error archiving exports: %s", e)


_LINK_STYLE_BASE = {"textDecoration": "none", "display": "block"}

if APP_MODE != 'runtime':
    @callback(
        Output("settings-button", "disabled"),
        Output("settings-button-link", "style"),
        Input("_pages_location", "pathname"),
        Input("timestamp", "data"),
        State("initial-bars", "data"),
    )
    def disable_button(pathname, timestamp, initial_bars):
        if pathname != "/":
            raise PreventUpdate
        # Locked once the session has moved past its starting candle
        is_disabled = timestamp != get_start_timestamp(get_market_dataframe(), initial_bars)
        return is_disabled, {**_LINK_STYLE_BASE, "pointerEvents": "none" if is_disabled else "auto"}


@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('portfolio-totals', 'data', allow_duplicate=True),
    Output('cost-basis', 'data', allow_duplicate=True),
    Output('nb_export', 'data'),
    Output('candle-step', 'data', allow_duplicate=True),
    Input('reset-button', 'n_clicks'),
    State('initial-cashflow', 'data'),
    State("nb_export", "data"),
    State('companies', 'data'),
    State('initial-bars', 'data'),
    prevent_initial_call=True,
)
def reset_data(btn, initial_cashflow, nb_export, companies_data, initial_bars=None):
    if btn is None or btn == 0:
        raise PreventUpdate

    threading.Thread(target=_archive_exports, args=(nb_export,), daemon=True).start()

    timestamp = get_start_timestamp(get_market_dataframe(), initial_bars)
    portfolio_value = {c: 0 for c, info in (companies_data or {}).items() if info.get('got_charts')}

    # candle-step None = the first candle is closed, like at session start
    return timestamp, initial_cashflow, [], portfolio_value, portfolio_value, {}, nb_export + 1, None


@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('portfolio-totals', 'data', allow_duplicate=True),
    Output('cost-basis', 'data', allow_duplicate=True),
    Output('nb_export', 'data', allow_duplicate=True),
    Output('do-redirect', 'data'),
    Output('session-start-time', 'data', allow_duplicate=True),
    Output('periodic-updater', 'disabled', allow_duplicate=True),
    Output('modal', 'opened', allow_duplicate=True),
    Output('pause-start-time', 'data', allow_duplicate=True),
    Output('total-paused-seconds', 'data', allow_duplicate=True),
    Output('nav-away-time', 'data', allow_duplicate=True),
    Output('candle-step', 'data', allow_duplicate=True),
    Input('reset-button-1', 'n_clicks'),
    State('initial-cashflow', 'data'),
    State("nb_export", "data"),
    State('companies', 'data'),
    State('initial-bars', 'data'),
    prevent_initial_call=True,
)
def reset_modal(btn, initial_cashflow, nb_export, companies_data, initial_bars):
    ts, cf, req, shares, totals, basis, nb, step = reset_data(btn, initial_cashflow, nb_export, companies_data, initial_bars)
    return ts, cf, req, shares, totals, basis, nb, True, None, False, False, None, 0, None, step


@callback(
    Output('cashflow', 'data', allow_duplicate=True),
    Input('initial-cashflow', 'data'),
    State('session-start-time', 'data'),
    State('requests', 'data'),
    State('portfolio-shares', 'data'),
    State('cashflow', 'data'),
    prevent_initial_call='initial_duplicate',
)
def start_cash_for_new_tab(initial_cashflow, session_start_time, requests, shares, cashflow):
    """A new tab (or new starting amount) starts with the session's starting money.

    Runs when a page opens and when the starting amount changes. Only while no
    game is in progress in this tab: session not started, no waiting orders and
    no shares held, so a refresh in the middle of a session never changes cash.
    """
    if initial_cashflow is None or session_start_time is not None:
        raise PreventUpdate
    if requests or any((shares or {}).values()):
        raise PreventUpdate
    if cashflow == initial_cashflow:
        raise PreventUpdate
    return initial_cashflow


@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('candle-step', 'data', allow_duplicate=True),
    Input('initial-bars', 'data'),
    State('session-start-time', 'data'),
    prevent_initial_call='initial_duplicate',
)
def apply_initial_bars(initial_bars, session_start_time):
    """Move the session's starting point when the number of history candles
    changes (Settings -> Advanced, an imported session, or the value saved in
    the browser). Never moves a session that has already started."""
    if session_start_time is not None:
        raise PreventUpdate
    return get_start_timestamp(get_market_dataframe(), initial_bars), None


clientside_callback(
    """function(doRedirect) {
        if (doRedirect) {
            window.history.pushState({}, '', '/');
            window.location.reload();
        }
        return false;
    }""",
    Output("do-redirect", "data", allow_duplicate=True),
    Input("do-redirect", "data"),
    prevent_initial_call=True,
)


@callback(
    Output("modal-pnl-content", "children"),
    Input("modal", "opened"),
    State("cashflow", "data"),
    State("portfolio-totals", "data"),
    State("portfolio-shares", "data"),
    State("initial-cashflow", "data"),
    State("companies", "data"),
    State("lang", "data"),
    prevent_initial_call=True,
)
def display_pnl_summary(opened, cashflow, totals, shares, initial, companies, lang):
    if not opened:
        raise PreventUpdate

    t = tls[lang or "fr"]["simulation-end"]

    cashflow = cashflow or 0
    totals = totals or {}
    shares = shares or {}
    initial = initial or dlt.initial_money

    stocks_value = sum(v for v in totals.values() if v is not None)
    final_value  = cashflow + stocks_value
    pnl          = final_value - initial
    pnl_pct      = (pnl / initial * 100) if initial else 0

    sign  = "+" if pnl >= 0 else ""
    color = "green" if pnl >= 0 else "red"

    def fmt(v):
        return f"{v:,.2f} €".replace(",", " ")

    # Per-stock rows — only companies with shares held
    rows = []
    for ticker, nb in shares.items():
        if nb <= 0:
            continue
        label = (companies or {}).get(ticker, {}).get("label", ticker)
        value = totals.get(ticker, 0)
        rows.append(
            html.Tr([
                html.Td(label, style={"paddingRight": "24px"}),
                html.Td(f"{nb} {t['shares']}", style={"paddingRight": "24px"}),
                html.Td(fmt(value), style={"textAlign": "right"}),
            ])
        )

    stock_table = dmc.Table(
        striped=True,
        children=[
            html.Thead(html.Tr([
                html.Th(t["col-company"]),
                html.Th(t["col-quantity"]),
                html.Th(t["col-value"], style={"textAlign": "right"}),
            ])),
            html.Tbody(rows if rows else [html.Tr([html.Td(t["no-position"], colSpan=3)])]),
        ]
    ) if rows or True else None

    return html.Div([
        # ── Summary cards ──────────────────────────────────────────
        html.Div([
            dmc.Paper([
                dmc.Text(t["initial-capital"], size="xs", color="dimmed"),
                dmc.Text(fmt(initial), weight=700, size="lg"),
            ], p="sm", radius="md", withBorder=True),

            dmc.Paper([
                dmc.Text(t["final-value"], size="xs", color="dimmed"),
                dmc.Text(fmt(final_value), weight=700, size="lg"),
            ], p="sm", radius="md", withBorder=True),

            dmc.Paper([
                dmc.Text(t["pnl"], size="xs", color="dimmed"),
                dmc.Text(f"{sign}{fmt(pnl)}", weight=700, size="lg", color=color),
                dmc.Text(f"{sign}{pnl_pct:.2f} %", size="xs", color=color),
            ], p="sm", radius="md", withBorder=True),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr 1fr", "gap": "12px", "marginBottom": "16px"}),

        # ── Cash vs stocks breakdown ───────────────────────────────
        html.Div([
            dmc.Paper([
                dmc.Text(t["cash"], size="xs", color="dimmed"),
                dmc.Text(fmt(cashflow), weight=700),
            ], p="sm", radius="md", withBorder=True),

            dmc.Paper([
                dmc.Text(t["stocks-value"], size="xs", color="dimmed"),
                dmc.Text(fmt(stocks_value), weight=700),
            ], p="sm", radius="md", withBorder=True),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "marginBottom": "16px"}),

        # ── Per-stock table ────────────────────────────────────────
        dmc.Text(t["breakdown-title"], weight=700, size="sm", style={"marginBottom": "8px"}),
        stock_table,
    ], style={"marginBottom": "16px"})