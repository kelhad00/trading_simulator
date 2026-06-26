import os
import threading

import dash_mantine_components as dmc
from dash import Output, Input, State, callback, clientside_callback, html, page_registry, ctx, no_update
from dash.exceptions import PreventUpdate

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.market import get_first_timestamp, get_market_dataframe
from trade.utils.news import get_news_dataframe
from trade.utils.settings.create_market_data import get_generated_data

market_df = get_market_dataframe()

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
        print("Error archiving exports:", e)


_LINK_STYLE_BASE = {"textDecoration": "none", "display": "block"}

if APP_MODE != 'runtime':
    @callback(
        Output("settings-button", "disabled"),
        Output("settings-button-link", "style"),
        Input("_pages_location", "pathname"),
        Input("timestamp", "data"),
    )
    def disable_button(pathname, timestamp):
        if pathname != "/":
            raise PreventUpdate
        is_disabled = timestamp != get_first_timestamp(market_df, 100)
        return is_disabled, {**_LINK_STYLE_BASE, "pointerEvents": "none" if is_disabled else "auto"}


@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('portfolio-totals', 'data', allow_duplicate=True),
    Output('nb_export', 'data'),
    Input('reset-button', 'n_clicks'),
    State('initial-cashflow', 'data'),
    State("nb_export", "data"),
    prevent_initial_call=True,
)
def reset_data(btn, initial_cashflow, nb_export):
    if btn is None or btn == 0:
        raise PreventUpdate

    threading.Thread(target=_archive_exports, args=(nb_export,), daemon=True).start()

    timestamp = get_first_timestamp(market_df, 100)
    df = get_generated_data()
    companies = df.columns.get_level_values('symbol').unique() if df is not None else []
    portfolio_value = {c: 0 for c in companies}

    return timestamp, initial_cashflow, [], portfolio_value, portfolio_value, nb_export + 1


@callback(
    Output('timestamp', 'data', allow_duplicate=True),
    Output('cashflow', 'data', allow_duplicate=True),
    Output('requests', 'data', allow_duplicate=True),
    Output('portfolio-shares', 'data', allow_duplicate=True),
    Output('portfolio-totals', 'data', allow_duplicate=True),
    Output('nb_export', 'data', allow_duplicate=True),
    Output('do-redirect', 'data'),
    Output('session-start-time', 'data', allow_duplicate=True),
    Output('periodic-updater', 'disabled', allow_duplicate=True),
    Output('modal', 'opened', allow_duplicate=True),
    Output('pause-start-time', 'data', allow_duplicate=True),
    Output('total-paused-seconds', 'data', allow_duplicate=True),
    Output('nav-away-time', 'data', allow_duplicate=True),
    Output('last-notified-ts', 'data', allow_duplicate=True),
    Input('reset-button-1', 'n_clicks'),
    State('initial-cashflow', 'data'),
    State("nb_export", "data"),
    prevent_initial_call=True,
)
def reset_modal(btn, initial_cashflow, nb_export):
    ts, cf, req, shares, totals, nb = reset_data(btn, initial_cashflow, nb_export)
    return ts, cf, req, shares, totals, nb, True, None, False, False, None, 0, None, None


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