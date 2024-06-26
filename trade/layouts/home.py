from dash import html, dcc, dash_table
from dash_iconify import DashIconify

from trade.Locales import translations as tls
from trade.candlestick_charts import PLOTLY_CONFIG
from trade.defaults import defaults as dlt

import dash_mantine_components as dmc

from trade.layouts.shared import header

import os


def main_layout(lang="fr"):

    button = disable_button()

    return html.Div([

        html.Div([
            header(lang),
            html.Div([
                welcome(lang),
                description(lang)
            ], className="flex flex-col gap-8"),
        ], className="flex flex-col gap-8"),

        options(button, lang)

    ], className="pt-8 pb-20 px-12 bg-gray-100 h-screen w-screen flex flex-col gap-8 justify-between")


def options(disable_button, lang="fr"):
    return html.Div([
        dmc.Button(
            dcc.Link(tls[lang]["button-start"], href="/dashboard?lang=" + lang),
            leftIcon=DashIconify(icon="carbon:play-filled-alt"),
            variant="solid", color="dark", radius="md", size="lg", disabled=disable_button,
        ),
        dmc.Button(
            dcc.Link(tls[lang]["button-settings"], href="/settings?lang=" + lang),
            leftIcon=DashIconify(icon="carbon:settings"),
            variant="solid", color="dark", radius="md", size="lg"
        ),
        dmc.Button(
            tls[lang]["button-restart-sim"],
            leftIcon=DashIconify(icon="carbon:reset"),
            variant="outline", color="dark", radius="md", size="lg", n_clicks=0),
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


def disable_button():
    if os.path.exists(os.path.join(dlt.data_path, 'generated_data.csv')):
        return False
    else:
        return True