from dash import html
import dash_mantine_components as dmc

from trade.layouts.settings.charts import generate_charts
from trade.layouts.settings.stocks import stocks_settings
from trade.layouts.shared import header

from trade.Locales import translations as tls


def main_layout(lang="fr"):
    return html.Div([
        header(lang, url="/settings"),
        dmc.Title(tls[lang]["settings-title"], order=1, className="font-bold leading-none w-full max-w-2xl"),
        dmc.Tabs(
            [
                dmc.TabsList([
                    dmc.Tab("Charts", value="charts"),
                    dmc.Tab("Stocks", value="stocks"),
                ], grow=True),

                dmc.TabsPanel(generate_charts(lang), value="charts"),
                dmc.TabsPanel(stocks_settings(lang), value="stocks"),
            ],
            # value="charts",
            value="stocks",
            color="dark",
            radius="md",
            className="w-full max-w-2xl flex flex-col gap-8"
        )
    ], className="px-12 p-8 bg-gray-100 flex flex-col items-center h-screen gap-8 overflow-auto"),




