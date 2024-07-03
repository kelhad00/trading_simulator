from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from trade.components.menu import lang_menu


def header(lang="fr", url="/"):
    return html.Div([
        dmc.Text(dcc.Link("TradeSim", href=f"/?lang={lang}"), className='font-bold text-xl'),
        html.Div([
            dmc.Button(
                dcc.Link("Github", href="https://github.com/kelhad00/trading_simulator", target="_blank"),
                color="dark",
                leftIcon=DashIconify(icon="mdi:github"),
                size="sm"
            ),
            lang_menu(lang, url)
        ], className="flex gap-4 items-center"),
    ], className="flex justify-between items-center w-full")
