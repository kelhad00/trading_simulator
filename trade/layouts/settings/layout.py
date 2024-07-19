from dash import html
import dash_mantine_components as dmc

from trade.layouts.settings.sections.advanced import advanced_settings
from trade.layouts.settings.sections.charts import generate_charts
from trade.layouts.settings.sections.stocks import stocks_settings
from trade.layouts.settings.sections.news import news_settings
from trade.layouts.settings.sections.import_settings import import_settings_layout
from trade.layouts.settings.sections.revenues import revenues_layout
from trade.components.header import header

from trade.locales import translations as tls




def main_layout(lang="fr"):
    return html.Div([
        header(lang, url="/settings"),
        dmc.Title(tls[lang]["settings-title"], order=1, className="font-bold leading-none w-full max-w-2xl"),
        dmc.Tabs(
            [
                dmc.TabsList([
                    dmc.Tab(tls[lang]["settings-tabs"]["import"], value="import"),
                    dmc.Tab(tls[lang]["settings-tabs"]["chart"], value="charts"),
                    dmc.Tab(tls[lang]["settings-tabs"]["stock"], value="stocks"),
                    dmc.Tab(tls[lang]["settings-tabs"]["news"], value="news"),
                    dmc.Tab(tls[lang]["settings-tabs"]["revenues"], value="revenues"),
                    dmc.Tab(tls[lang]["settings-tabs"]["advanced"], value="advanced"),
                ], grow=True),

                dmc.TabsPanel(import_settings_layout(lang), value="import"),
                dmc.TabsPanel(generate_charts(lang), value="charts"),
                dmc.TabsPanel(stocks_settings(lang), value="stocks"),
                dmc.TabsPanel(news_settings(lang), value="news"),
                dmc.TabsPanel(revenues_layout(lang), value="revenues"),
                dmc.TabsPanel(advanced_settings(lang), value="advanced"),
            ],
            # value="charts",
            value="revenues",
            id="settings-tabs",
            color="dark",
            radius="md",
            className="w-full max-w-2xl flex flex-col gap-8"
        )
    ], className="px-12 p-8 bg-gray-100 flex flex-col items-center h-screen gap-8 overflow-auto"),




