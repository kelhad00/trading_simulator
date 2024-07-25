from dash import html, dcc
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import os

from trade.locales import translations as tls
from trade.defaults import defaults as dlt

from trade.components.header import header


def main_layout(lang="fr"):
    return html.Div([
        html.Div([
            # Application url for routing when the user clicks on the start button
            header(lang),
            html.Div([
                welcome(lang),
                description(lang)
            ], className="flex flex-col gap-8"),
        ], className="flex flex-col gap-8"),
        options(lang)
    ], className="pt-8 pb-20 px-12 bg-gray-100 h-screen w-screen flex flex-col gap-8 justify-between")


def options(lang="fr"):
    disabled = disable_button()

    def option(label, href, icon, disabled=False, id=""):
        return dmc.Button(
            dcc.Link(label, href=href),
            id=id,
            leftIcon=DashIconify(icon=icon),
            variant="solid", color="dark", radius="md", size="lg", disabled=disabled
        )

    return html.Div([
        option(tls[lang]["button-start"], "/dashboard?lang=" + lang, "carbon:play-filled-alt", disabled),
        option(tls[lang]["button-settings"], "/settings?lang=" + lang, "carbon:settings", id="settings-button"),
        dmc.Button(tls[lang]["button-restart-sim"], leftIcon=DashIconify(icon="carbon:reset"), id="reset-button", color="dark", size="lg")

    ], className="flex gap-4 flex-col max-w-xs")


def description(lang="fr"):
    def variant(content):
        return html.Span(content, className="text-3xl font-semibold text-[rgb(73,80,87)]")

    return dmc.Text([
        tls[lang]["description"][0],
        variant(tls[lang]["description"][1]),
        tls[lang]["description"][2],
        variant(tls[lang]["description"][3]),
        tls[lang]["description"][4],
        variant(tls[lang]["description"][5]),
        tls[lang]["description"][6],
    ], className="text-3xl font-semibold max-w-2xl")


def welcome(lang="fr"):
    className = "text-8xl font-bold leading-none"
    return html.Div([
        dmc.Title(tls[lang]["welcome"][0], order=1, className=f"{className} text-[rgb(73,80,87)]"),
        dmc.Title(tls[lang]["welcome"][1], order=1, className=className),
    ])


def disable_button():
    if os.path.exists(os.path.join(dlt.data_path, 'generated_data.csv')) and os.path.exists(os.path.join(dlt.data_path, 'news.csv')):
        return False
    else:
        return True