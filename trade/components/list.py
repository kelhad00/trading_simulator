import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from trade.locales import translations as tls
def stock_list_element(stock, company, lang="fr"):
    return dmc.Paper([
        html.Div([

            dmc.Text(tls[lang]["settings"]["tickers"]["input"]["ticker"], weight=500),
            dmc.Text(stock, size="sm"),
        ], className="flex flex-col flex-1"),
        html.Div([
            dmc.Text(tls[lang]["settings"]["tickers"]["input"]["company"], weight=500),
            dmc.Text(company, size="sm"),
        ], className="flex flex-col flex-[2]"),
        dmc.ActionIcon(
            DashIconify(icon="material-symbols:delete-outline", width=20),
            size="lg",
            radius="md",
            color="dark",
            variant="outline",
            id={"type": "delete-stock", "index": stock},
            n_clicks=0,
        ),
    ],
        className="flex justify-between gap-4 items-center",
        radius="md",
        p="xs",
        withBorder=True,
    )

