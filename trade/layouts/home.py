from dash import html, dcc, dash_table
from dash_iconify import DashIconify

from trade.Locales import translations as tls
from trade.candlestick_charts import PLOTLY_CONFIG
from trade.defaults import defaults as dlt

import dash_mantine_components as dmc

from trade.layouts.shared import header


def main_layout(lang="fr"):
    return html.Div([

        html.Div([
            header(lang),
            html.Div([
                welcome(lang),
                description(lang)
            ], className="flex flex-col gap-8"),
        ], className="flex flex-col gap-8"),

        options(lang)

    ], className="pt-8 pb-20 px-12 bg-gray-100 h-screen w-screen flex flex-col gap-8 justify-between")


def options(lang="fr"):
    return html.Div([
        dmc.Button(
            dcc.Link(tls[lang]["button-start"], href="/dashboard?lang=" + lang),
            variant="solid", color="dark", radius="md", size="lg"
        ),
        dmc.Button(
            dcc.Link(tls[lang]["button-settings"], href="/settings?lang=" + lang),
            variant="solid", color="dark", radius="md", size="lg"
        ),
        dmc.Button(tls[lang]["button-restart-sim"], variant="outline", color="dark", radius="md", size="lg", n_clicks=0, id="reset-button"),
    ], className="flex gap-4 flex-col max-w-xs")


def description(lang="fr"):
    return dmc.Text([
        tls[lang]["description"][0],
        html.Span(tls[lang]["description"][1], className="text-3xl font-semibold text-[rgb(73,80,87)]"),
        tls[lang]["description"][2],
        html.Span(tls[lang]["description"][3], className="text-3xl font-semibold text-[rgb(73,80,87)]"),
        tls[lang]["description"][4],
        html.Span(tls[lang]["description"][5], className="text-3xl font-semibold text-[rgb(73,80,87)]"),
        tls[lang]["description"][6],
    ], className="text-3xl font-semibold max-w-2xl")


def welcome(lang="fr"):
    return html.Div([
        dmc.Title(tls[lang]["welcome"][0], order=1, className="text-8xl font-bold text-[rgb(73,80,87)] leading-none	"),
        dmc.Title(tls[lang]["welcome"][1], order=1, className="text-8xl font-bold leading-none	"),
    ])


