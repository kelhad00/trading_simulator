from dash import html
import dash_mantine_components as dmc

from trade.layouts.settings.sections.advanced import advanced_settings
from trade.layouts.settings.sections.charts import generate_charts
from trade.layouts.settings.sections.stocks import stocks_settings
from trade.layouts.settings.sections.news import news_settings
from trade.components.header import header

from trade.locales import translations as tls


def main_layout(lang="fr"):
    return html.Div([
        header(lang, url="/settings"),
        dmc.Title(tls[lang]["settings-title"], order=1, className="font-bold leading-none w-full max-w-2xl"),
        dmc.Tabs(
            [
                dmc.TabsList([
                    dmc.Tab(tls[lang]["settings-tabs"]["chart"], value="charts"),
                    dmc.Tab(tls[lang]["settings-tabs"]["stock"], value="stocks"),
                    dmc.Tab(tls[lang]["settings-tabs"]["news"], value="news"),
                    dmc.Tab(tls[lang]["settings-tabs"]["advanced"], value="advanced"),
                ], grow=True),

                dmc.TabsPanel(generate_charts(lang), value="charts"),
                dmc.TabsPanel(stocks_settings(lang), value="stocks"),
                dmc.TabsPanel(news_settings(lang), value="news"),
                dmc.TabsPanel(advanced_settings(lang), value="advanced"),
            ],
            value="charts",
            id="settings-tabs",
            color="dark",
            radius="md",
            className="w-full max-w-2xl flex flex-col gap-8"
        )
    ], className="px-12 p-8 bg-gray-100 flex flex-col items-center h-screen gap-8 overflow-auto"),




