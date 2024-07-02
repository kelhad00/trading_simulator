from dash import html
import dash_mantine_components as dmc

from trade.locales import translations as tls

def portfolio(lang="fr"):
    return html.Div([
        html.Div([
            portfolio_section(tls[lang]['portfolio-cashflow'], "portfolio-cashflow"),
            portfolio_section(tls[lang]['portfolio-investment'], "portfolio-investment"),
        ], className="flex gap-2 justify-between flex-wrap"),
        portfolio_table(lang),
    ], className="col-span-2 row-span-3 flex flex-col gap-2 h-full w-full")


def portfolio_section(label, id):
    return dmc.Paper(
        className="flex-1 flex flex-col gap-2 justify-between",
        children=[
            dmc.Text(label, weight=700, className="text-[rgb(73,80,87)] text-ellipsis leading-none", size="sm"),
            dmc.Text(weight=500, size="xl", id=id),
        ]
    )


def portfolio_table(lang="fr"):
    return dmc.Paper(
        className="flex-1 overflow-hidden flex flex-col gap-2",
        children=[
            dmc.Text(tls[lang]['portfolio'], weight=700, className="text-[rgb(73,80,87)]", size="xl"),
            html.Div(id='portfolio-table-container', className="h-full w-full overflow-y-scroll"),
        ]
    )

