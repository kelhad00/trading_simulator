from dash import Output, Input, State, callback, page_registry, ctx, html, ALL, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from trade.locales import translations as tls

import pandas as pd


def _colored_amount(value, reference):
    color = "green" if value > reference else "red" if value < reference else None
    text = f"{round(value, 2)}€"
    return html.Span(text, style={"color": color, "fontWeight": "bold"}) if color else text


@callback(
    Output('portfolio-cashflow', 'children'),
    Output('portfolio-investment', 'children'),
    Input('periodic-updater', 'n_intervals'),
    Input('portfolio-totals', 'data'),
    Input('cashflow', 'data'),
    State('initial-cashflow', 'data'),
)
def display_portfolio_updated(n, totals, cashflow, initial_cashflow):
    totals = pd.Series(totals)
    investment = cashflow + totals.sum()
    ref = initial_cashflow or 0
    return _colored_amount(cashflow, ref), _colored_amount(investment, ref)


@callback(
    Output("portfolio-table-container", "children"),
    Input('periodic-updater', 'n_intervals'),
    Input('portfolio-totals', 'data'),
    Input('portfolio-shares', 'data'),
    Input('company-selector', 'value'),
    State('cost-basis', 'data'),
    State('sold-data', 'data'),
)
def display_portfolio_table_updated(n, totals, shares, selected_company, cost_basis, sold_data):
    """
    Display the updated portfolio table
    Args:
        totals: The portfolio totals
        shares: The portfolio shares
    Returns:
        The updated portfolio table
    """

    lang = page_registry.get('lang', 'fr')
    cost_basis = dict(cost_basis or {})
    sold_data = dict(sold_data or {})
    cols = tls[lang]['portfolio-columns']

    totals = pd.Series(totals).fillna(0)
    shares = pd.Series(shares)

    def fmt(value):
        return f"{value:.2f}€"

    header = html.Thead(html.Tr([
        html.Th(cols['Stock']),
        html.Th(cols['Shares']),
        html.Th(cols['Total']),
        html.Th(cols['CurPrice']),
        html.Th(cols['BoughtAt']),
        html.Th(cols['SoldAt']),
        html.Th(cols['PnL']),
    ]))
    rows = []
    for ticker in shares.index:
        shares_held = shares.get(ticker, 0)
        basis = cost_basis.get(ticker, 0)
        total_val = totals.get(ticker, 0)

        cur_price = fmt(total_val / shares_held) if shares_held > 0 else "-"
        avg_buy = fmt(basis / shares_held) if shares_held > 0 else "-"
        sd = sold_data.get(ticker, {})
        avg_sell = fmt(sd["revenue"] / sd["shares"]) if sd.get("shares", 0) > 0 else "-"
        pnl_val = total_val - basis
        pnl_color = "green" if pnl_val > 0 else "red" if pnl_val < 0 else None
        pnl_cell = html.Span(fmt(pnl_val), style={"color": pnl_color, "fontWeight": "bold"}) if pnl_color else fmt(pnl_val)

        if shares_held > 0 and basis > 0:
            row_color = "green" if total_val >= basis else "red"
        else:
            row_color = None
        style = {"cursor": "pointer"}
        if row_color:
            style["color"] = row_color
        if ticker == selected_company:
            style["backgroundColor"] = "#e7f5ff"
        rows.append(html.Tr(
            children=[
                html.Td(ticker),
                html.Td(shares_held),
                html.Td(fmt(total_val)),
                html.Td(cur_price),
                html.Td(avg_buy),
                html.Td(avg_sell),
                html.Td(pnl_cell),
            ],
            id={"type": "portfolio-row", "index": ticker},
            n_clicks=0,
            style=style,
        ))

    return dmc.Table(
        highlightOnHover=True,
        children=[header, html.Tbody(rows)],
    )


@callback(
    Output('company-selector', 'value', allow_duplicate=True),
    Input({"type": "portfolio-row", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def select_company_from_portfolio(clicks):
    if not any(clicks):
        raise PreventUpdate
    return ctx.triggered_id['index']


