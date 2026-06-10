from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from trade.components.menu import lang_menu
from trade.locales import translations as tls


def header(lang="fr", url="/", mode=None):
    badge = (
        dmc.Badge(
            tls[lang].get(f"mode-{mode}", mode),
            color="grape" if mode == "config" else "blue",
            variant="light",
            size="md",
        )
        if mode else None
    )

    logo = html.Div(
        [dmc.Text(dcc.Link("TradeSim", href=f"/?lang={lang}"), className='font-bold text-xl'), badge],
        className="flex items-center gap-3"
    ) if badge else dmc.Text(dcc.Link("TradeSim", href=f"/?lang={lang}"), className='font-bold text-xl')

    return html.Div([
        logo,
        html.Div([
            html.A(
                dmc.Button(
                    "Github",
                    color="dark",
                    leftIcon=DashIconify(icon="mdi:github"),
                    size="sm"
                ),
                href="https://github.com/kelhad00/trading_simulator",
                target="_blank",
                style={"textDecoration": "none", "display": "inline-flex"}
            ),
            lang_menu(lang, url)
        ], className="flex gap-4 items-center"),
    ], className="flex justify-between items-center w-full")
