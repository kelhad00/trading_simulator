from dash import html, dcc
import dash_mantine_components as dmc

from trade.layouts.dashboard.sections.graph import graph
from trade.layouts.dashboard.sections.news import news, news_description
from trade.layouts.dashboard.sections.portfolio import portfolio
from trade.layouts.dashboard.sections.requests import request
from trade.locales import translations as tls


def main_layout(lang="fr"):
    t = tls[lang]["simulation-end"]
    ctx_t = tls[lang]["ctx-menu"]
    return html.Div([
        dcc.Interval(id='periodic-updater', interval=5000, n_intervals=0, disabled=False),
        dcc.Store(id='lang', data=lang),
        dcc.Store(id='description-ticker', data=None),

        # Right-click context menu — position:fixed so it floats above everything
        html.Div(
            id="chart-context-menu",
            style={
                "display": "none",
                "position": "fixed",
                "zIndex": 9999,
                "backgroundColor": "white",
                "border": "1px solid #dee2e6",
                "borderRadius": "6px",
                "padding": "4px",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.15)",
                "flexDirection": "column",
                "gap": "2px",
                "minWidth": "140px",
            },
            children=[
                dmc.Button(ctx_t["buy"], id="ctx-buy-btn", color="green", size="xs", variant="subtle", fullWidth=True),
                dmc.Button(ctx_t["sell"], id="ctx-sell-btn", color="red", size="xs", variant="subtle", fullWidth=True),
            ]
        ),

        dmc.Modal(
            id="modal",
            title=dmc.Title(t["title"], order=2, className="font-bold w-full max-w-2xl"),
            className="flex flex-col gap-8",
            radius="md",
            zIndex=10000,
            size="lg",
            children=[
                html.Div(id="modal-pnl-content"),
                dmc.Button(t["validate"], color='dark', id="reset-button-1", n_clicks=0),
            ]
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



