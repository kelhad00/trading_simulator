from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify



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


def dashboard_menu(lang="fr"):
    en_bg = ""
    fr_bg = ""

    if lang == "fr":
        fr_bg = "bg-gray-100"
    else:
        en_bg = "bg-gray-100"

    return dmc.Menu(
        [
            dmc.MenuTarget(
                dmc.ActionIcon(
                    DashIconify(icon="carbon:settings"),
                    size="lg",
                    variant="outline",
                )
            ),
            dmc.MenuDropdown(
                [
                    dmc.MenuLabel("Simulation"),
                    dmc.MenuItem("Pause", icon=DashIconify(icon="carbon:pause"), id="pause-button",
                                 href=f"/?lang={lang}"),
                    dmc.MenuItem("Reset", icon=DashIconify(icon="carbon:reset"), id="reset-button", n_clicks=0,
                                 color="red"),
                    dmc.MenuDivider(),
                    dmc.MenuLabel("Language"),
                    dmc.MenuItem("Français", icon=DashIconify(icon="twemoji:flag-france"),
                                 href="/dashboard?lang=fr", n_clicks=0, className=fr_bg),
                    dmc.MenuItem("English", icon=DashIconify(icon="twemoji:flag-united-states"),
                                 href="/dashboard?lang=en", n_clicks=0, className=en_bg),
                ],
            )
        ], position="left-start"
    )
