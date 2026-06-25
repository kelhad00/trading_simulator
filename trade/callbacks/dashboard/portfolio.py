from dash import Output, Input, State, callback, page_registry, ctx, html, ALL, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from trade.locales import translations as tls

import pandas as pd


@callback(
    Output('portfolio-cashflow', 'children'),
    Output('portfolio-investment', 'children'),
    Input('periodic-updater', 'n_intervals'),
    Input('portfolio-totals', 'data'),
    Input('cashflow', 'data'),
)
def display_portfolio_updated(n, totals, cashflow):
    """
    Display the portfolio cashflow and investment updated
    Args:
        totals: The portfolio totals
        cashflow: The portfolio cashflow
    Returns:
        The updated portfolio cashflow and investment
    """
    totals = pd.Series(totals)
    return f"{round(cashflow, 2)}€", f"{round(cashflow + totals.sum(), 2)}€"


@callback(
    Output("portfolio-table-container", "children"),
    Input('periodic-updater', 'n_intervals'),
    Input('portfolio-totals', 'data'),
    Input('portfolio-shares', 'data'),
)
def display_portfolio_table_updated(n, totals, shares):
    """
    Display the updated portfolio table
    Args:
        totals: The portfolio totals
        shares: The portfolio shares
    Returns:
        The updated portfolio table
    """

    lang = page_registry['lang']

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
    rows = [
        html.Tr(
            children=[html.Td(cell) for cell in row],
            id={"type": "portfolio-row", "index": row[0]},
            n_clicks=0,
            style={"cursor": "pointer"},
        )
        for row in df.values
    ]

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


