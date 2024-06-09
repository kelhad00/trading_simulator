from dash import html, dcc, dash_table
from dash_iconify import DashIconify

from trade.Locales import translations as tls
from trade.candlestick_charts import PLOTLY_CONFIG
from trade.defaults import defaults as dlt

import dash_mantine_components as dmc


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
        dmc.Button(tls[lang]["button-restart-sim"], variant="outline", color="dark", radius="md", size="lg", n_clicks=0, id="restart_simu"),
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


def header(lang="fr"):
    return html.Div([
        dmc.Text("TradeSim", className='font-bold text-xl'),
        html.Div([
            dmc.Button(
                dcc.Link("Github", href="https://github.com/kelhad00/trading_simulator", target="_blank"), color="dark", radius="md", leftIcon=DashIconify(icon="mdi:github"), size="sm"),
            menu(lang)
        ], className="flex gap-4 items-center"),
    ], className="flex justify-between")


def menu(lang="fr"):
    en_bg = ""
    fr_bg = ""

    if lang == "fr" :
        icon = "twemoji:flag-france"
        fr_bg = "bg-gray-100"
    else:
        icon = "twemoji:flag-united-states"
        en_bg = "bg-gray-100"

    return dmc.Menu(
        [
            dmc.MenuTarget(
                dmc.ActionIcon(
                    DashIconify(icon=icon),
                    size="lg",
                    radius="md",
                    variant="outline",
                    color="dark",
                    className="h-full"
                )
            ),
            dmc.MenuDropdown(
                [
                    dmc.MenuLabel("Language"),
                    dmc.MenuItem("Français", icon=DashIconify(icon="twemoji:flag-france"), href="/?lang=fr", n_clicks=0, className=fr_bg),
                    dmc.MenuItem("English", icon=DashIconify(icon="twemoji:flag-united-states"), href="/?lang=en", n_clicks=0, className=en_bg),
                ], pos="bottom-end"
            )
        ]
    )