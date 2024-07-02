from dash import html
import dash_mantine_components as dmc

from trade.components.sections import section
from trade.locales import translations as tls


def stocks_settings(lang="fr"):
    return html.Div([
        section(tls[lang]["settings-subtitles"]["charts-patterns"], [
            html.Div([
                dmc.Select(
                    id="input-company",
                    label="Company",
                    creatable=True,
                    searchable=True,
                    className="flex-1"
                ),
                html.Div([
                    dmc.TextInput(
                        id="input-stock",
                        label="Ticker",
                        className="flex-1"
                    ),
                    dmc.Select(
                        id="input-activity",
                        label="Activity",
                        className="flex-1"
                    ),
                ], className="flex gap-4 w-full justify-between"),
            ], className="flex flex-col gap-2"),

            dmc.Button("Add", id="add-company", color="dark", size="md"),
        ]),
        section(tls[lang]["settings-subtitles"]["charts-patterns"], [
            html.Div(id="list-companies", className="flex flex-col gap-4"),
        ]),


    ], className="flex flex-col gap-8 w-full")
