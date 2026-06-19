import os
from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from trade.layouts.settings.sections.advanced import advanced_settings
from trade.layouts.settings.sections.charts import generate_charts
from trade.layouts.settings.sections.stocks import stocks_settings
from trade.layouts.settings.sections.news import news_settings
from trade.layouts.settings.sections.import_settings import import_settings_layout
from trade.layouts.settings.sections.revenues import revenues_layout
from trade.components.header import header

from trade.locales import translations as tls

APP_MODE = os.getenv('APP_MODE', 'config')


def main_layout(lang="fr"):
    tl = tls[lang]["settings"]

    return html.Div([
        header(lang, url="/settings", mode=APP_MODE),
        html.Div([
            dmc.Title(tl["title"], order=1, className="font-bold leading-none"),
            dmc.Button(
                tls[lang]["session"]["export-button"],
                id="export-session-btn",
                leftIcon=DashIconify(icon="carbon:export"),
                variant="outline",
                color="dark",
                radius="md",
                disabled=True,
            ),
        ], className="flex items-center justify-between w-full max-w-2xl"),
        dmc.Tabs(
            [
                dmc.TabsList([
                    dmc.Tab(tl["tabs"]["import"], value="import"),
                    dmc.Tab(tl["tabs"]["chart"], value="charts"),
                    dmc.Tab(tl["tabs"]["ticker"], value="tickers"),
                    dmc.Tab(tl["tabs"]["news"], value="news"),
                    dmc.Tab(tl["tabs"]["revenues"], value="revenues"),
                    dmc.Tab(tl["tabs"]["advanced"], value="advanced"),
                ], grow=True),

                dmc.TabsPanel(import_settings_layout(lang), value="import"),
                dmc.TabsPanel(generate_charts(lang), value="charts"),
                dmc.TabsPanel(stocks_settings(lang), value="tickers"),
                dmc.TabsPanel(news_settings(lang), value="news"),
                dmc.TabsPanel(revenues_layout(lang), value="revenues"),
                dmc.TabsPanel(advanced_settings(lang), value="advanced"),
            ],
            value="charts",
            id="settings-tabs",
            color="dark",
            radius="md",
            className="w-full max-w-2xl flex flex-col gap-8"
        )
    ], className="px-12 p-8 bg-gray-100 flex flex-col items-center h-screen gap-8 overflow-auto"),




