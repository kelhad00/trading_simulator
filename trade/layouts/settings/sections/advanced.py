from dash import html
import dash_mantine_components as dmc

from trade.locales import translations as tls
from trade.defaults import defaults as dlt
from trade.components.sections import section


def advanced_settings(lang="fr"):
    return html.Div([
        section(tls[lang]["settings-subtitles"]["advanced-init"], [
            html.Div([
                dmc.TextInput(
                    id="input-update-time",
                    label=tls[lang]["settings-advanced-init-input"]["update-time"],
                    required=True
                ),
                dmc.NumberInput(
                    id="input-max-requests",
                    label=tls[lang]["settings-advanced-init-input"]["requests"],
                    required=True,
                    min=1,
                    max=100
                ),
                dmc.NumberInput(
                    id="input-init-cashflow",
                    label=tls[lang]["settings-advanced-init-input"]["cashflow"],
                    required=True,
                    min=1,
                ),
            ], className="flex flex-col gap-2"),

            dmc.Button(tls[lang]["settings-button"]["update"], id="update-advanced-settings", color="dark", size="md"),
        ]),
    ], className="flex flex-col gap-8 w-full")