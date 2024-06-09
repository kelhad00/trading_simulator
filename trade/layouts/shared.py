from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

def header(lang="fr", url="/"):
    return html.Div([
        dmc.Text(dcc.Link("TradeSim", href=f"/?lang={lang}"), className='font-bold text-xl'),
        html.Div([
            dmc.Button(
                dcc.Link("Github", href="https://github.com/kelhad00/trading_simulator", target="_blank"), color="dark", radius="md", leftIcon=DashIconify(icon="mdi:github"), size="sm"),
            lang_menu(lang, url)
        ], className="flex gap-4 items-center"),
    ], className="flex justify-between items-center w-full")


def lang_menu(lang="fr", url="/" ):
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
                    dmc.MenuItem("Français", icon=DashIconify(icon="twemoji:flag-france"), href=f"{url}?lang=fr", n_clicks=0, className=fr_bg),
                    dmc.MenuItem("English", icon=DashIconify(icon="twemoji:flag-united-states"), href=f"{url}?lang=en", n_clicks=0, className=en_bg),
                ], pos="bottom-end"
            )
        ]
    )