from dash import html, dcc
import dash_mantine_components as dmc

from trade.layouts.dashboard.sections.graph import graph
from trade.layouts.dashboard.sections.news import news, news_description
from trade.layouts.dashboard.sections.portfolio import portfolio
from trade.layouts.dashboard.sections.requests import request


def main_layout(lang="fr"):
    return html.Div([
        dcc.Interval(id='periodic-updater', interval=5000),
        dmc.Modal(
            id="modal",
            title=dmc.Title("Simulation terminée !", order=2, className="font-bold w-full max-w-2xl"),
            className="flex flex-col gap-8",
            radius="md",
            zIndex=10000,
            children=dmc.Button("Valider", color='dark', id="reset-button-1", n_clicks=0)  # dcc.Link('Valider', href="/")
        ),
        html.Div(id="export", className="hidden"),
        html.Div([
            portfolio(lang),
            graph(lang),
            news(lang),
            news_description(lang),
            request(lang)
        ], className="grid grid-cols-7 grid-rows-5 gap-4 h-screen w-screen bg-gray-100 p-4")
    ])



