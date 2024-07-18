from dash import html
import dash_mantine_components as dmc

from trade.components.radio import radio
from trade.components.sections import section
from trade.locales import translations as tls

def revenues_layout(lang="fr"):
    return html.Div([
        section("Configuration", [
            dmc.Select(
                id="revenues-select-company",
                label=tls[lang]["settings-number-inputs"]["number-patterns"],
                className="w-full"
            ),
            radio(
                options=[("auto", "Auto"), ("manual", "Manual")],
                label="Choose a mode",
                value="auto",
                id="input-revenue-mode",
            ),
            html.Div(id="revenues-inputs-container")
        ]),
        dmc.Button(tls[lang]["settings-button"]["generate"], id="generate-revenue", color="dark", size="md"),

    ], className="flex flex-col gap-8 w-full")
