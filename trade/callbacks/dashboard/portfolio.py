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
    State('cost-basis', 'data'),
)
def display_portfolio_table_updated(n, totals, shares, cost_basis):
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

    totals = pd.Series(totals).fillna(0)
    shares = pd.Series(shares)
    df = pd.concat([shares, totals], axis=1)  # Concatenate the shares and totals

    # Rename the columns for the display in the table
    df.columns = [tls[lang]['portfolio-columns']['Shares'], tls[lang]['portfolio-columns']['Total']]

    # Reset the index to put each Stock as an index and rename the column to 'Stock'
    df.reset_index(inplace=True)
    df.rename(columns={'index': tls[lang]['portfolio-columns']['Stock']}, inplace=True)

    # Round totals to 2 decimal places
    df[tls[lang]['portfolio-columns']['Total']] = df[tls[lang]['portfolio-columns']['Total']].round(2)

    header = html.Thead(html.Tr([html.Th(col) for col in df.columns]))
    rows = []
    for row in df.values:
        ticker = row[0]
        shares_held = shares.get(ticker, 0)
        basis = cost_basis.get(ticker, 0)
        total_val = totals.get(ticker, 0)
        if shares_held > 0 and basis > 0:
            row_color = "green" if total_val >= basis else "red"
        else:
            row_color = None
        rows.append(html.Tr(
            children=[html.Td(cell) for cell in row],
            id={"type": "portfolio-row", "index": ticker},
            n_clicks=0,
            style={"cursor": "pointer", "color": row_color} if row_color else {"cursor": "pointer"},
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


