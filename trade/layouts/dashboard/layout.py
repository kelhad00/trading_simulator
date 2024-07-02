from dash import html, dcc, dash_table
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from trade.layouts.dashboard.sections.graph import graph
from trade.layouts.dashboard.sections.news import news, news_description
from trade.layouts.dashboard.sections.portfolio import portfolio
from trade.layouts.dashboard.sections.requests import request
from trade.locales import translations as tls
from trade.candlestick_charts import PLOTLY_CONFIG
from trade.defaults import defaults as dlt

from trade.components.menu import dashboard_menu as menu



def main_layout(lang="fr"):
    return html.Div(
        html.Div([
            dcc.Interval(id='periodic-updater', interval=5000),
            html.Div([
                portfolio(lang),
                graph(lang),
                news(lang),
                news_description(lang),
                request(lang)
            ], className="grid grid-cols-7 grid-rows-5 gap-4 h-screen w-screen bg-gray-100 p-4")
        ]))



