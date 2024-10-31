from dash import html
import dash_mantine_components as dmc

from trade.components.sections import section
from trade.locales import translations as tls


def stocks_settings(lang="fr"):
    tl = tls[lang]["settings"]["tickers"]
    return html.Div([
        section(tl["subtitles"]["form"], [
            html.Div([
                dmc.Select(
                    id="input-company",
                    label=tl["input"]["company"],
                    creatable=True,
                    searchable=True,
                    className="flex-1"
                ),
                html.Div([
                    dmc.TextInput(
                        id="input-stock",
                        label=tl["input"]["ticker"],
                        className="flex-1"
                    ),
                    dmc.Select(
                        id="input-activity",
                        label=tl["input"]["activity"],
                        # creatable=True,
                        searchable=True,
                        className="flex-1"
                    ),
                ], className="flex gap-4 w-full justify-between"),
            ], className="flex flex-col gap-2"),

            dmc.Button(tl["button"]["add"], id="add-company", color="dark", size="md"),
        ]),
        section(tl["subtitles"]["list"], [
            html.Div(id="list-companies", className="flex flex-col gap-4"),
        ], action_id="reset-stocks", action="Reset"),


    ], className="flex flex-col gap-8 w-full")
