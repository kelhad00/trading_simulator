from dash import html
import dash_mantine_components as dmc

from trade.layouts.shared import header


def main_layout(lang="fr"):
    return html.Div([
        header(lang, url="/settings"),
        dmc.Title("Settings", order=1, className="font-bold leading-none w-full max-w-2xl"),

        html.Div([
            dmc.Text("Market Data Creation", weight=700, className="text-[rgb(73,80,87)]", size="xl"),

            html.Div([
                dmc.Text("Select alpha", weight=500,
                         className="text-[rgb(73,80,87)] text-ellipsis leading-none", size="sm"),
                dmc.Slider(
                    id="slider-callback",
                    value=26,
                    max=2000,
                    min=0,
                    color="dark",
                    marks=[
                        {"value": 0, "label": "0"},
                        {"value": 1000, "label": "1000"},
                        {"value": 2000, "label": "2000"},
                    ],
                    className="mb-4"
                ),
            ], className="flex flex-col gap-2 w-full"),
            html.Div([
                dmc.Text("Select length", weight=500,
                         className="text-[rgb(73,80,87)] text-ellipsis leading-none", size="sm"),
                dmc.Slider(
                    id="slider-callback",
                    value=26,
                    max=2000,
                    min=0,
                    color="dark",
                    marks=[
                        {"value": 0, "label": "0"},
                        {"value": 1000, "label": "1000"},
                        {"value": 2000, "label": "2000"},
                    ],
                    className="mb-4"
                ),
            ], className="flex flex-col gap-2 w-full"),
        ], className="flex flex-col gap-4 max-w-2xl w-full items-start"),

        html.Div([
            dmc.Text("Charts trends", weight=700, className="text-[rgb(73,80,87)]", size="xl"),
        ], className="flex flex-col gap-4 max-w-2xl w-full items-start"),



    ], className="p-8 px-12 bg-gray-100 h-screen w-screen flex flex-col items-center gap-8")


