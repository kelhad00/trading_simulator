from dash import html, dcc
import dash_mantine_components as dmc

from trade.components.sections import section
from trade.locales import translations as tls
from trade.defaults import Defaults as dlt


def news_settings(lang="fr"):
    tl = tls[lang]["settings"]["news"]
    return html.Div([
        section(tl["subtitles"]["key"], [
            html.Div([
                dmc.TextInput(
                    id="input-api-key",
                    label=tl["input"]["key"],
                    className="flex-1",
                    value=dlt.api_key
                ),
            ], className="flex w-full"),
        ]),
        section(tl["subtitles"]["parameters"], [
            html.Div([
                dmc.NumberInput(
                    id="input-alpha",
                    label=tl["input"]["alpha"],
                    className="flex-1",
                    value=3,
                ),
            ], className="flex w-full"),

            html.Div([
                dmc.NumberInput(
                    id="input-alpha-day-interval",
                    label=tl["input"]["alpha-day-interval"],
                    className="flex-1",
                    value=3,
                ),
            ], className="flex w-full"),

            html.Div([
                dmc.NumberInput(
                    id="input-delta",
                    label=tl["input"]["delta"],
                    className="flex-1",
                    value=0,
                ),
            ], className="flex w-full"),
        ]),

        section(tl["subtitles"]["mode"], [
            html.Div([
                dmc.RadioGroup(
                    id="input-generation-mode",
                    label=tl["radio"]["label"],
                    children=[
                        dmc.Radio(value="random", label=tl["radio"]["options"][0]),
                        dmc.Radio(value="linear", label=tl["radio"]["options"][1]),
                    ],
                    value="random",
                ),
            ], className="flex w-full"),

            # Display the number of news input only in random mode
            html.Div([
                dmc.NumberInput(
                    id="input-nbr-positive-news",
                    label=tl["input"]["nbr-positive-news"],
                    className="flex-1",
                    value=5,
                ),
                dmc.NumberInput(
                    id="input-nbr-negative-news",
                    label=tl["input"]["nbr-negative-news"],
                    className="flex-1",
                    value=5,
                ),
            ], className="flex w-full", id="nbr-news-container"),
        ]),


        section(tl["subtitles"]["preview"], [
            dmc.Select(
                id="news-select-company",
                label=tl["select"]["ticker"],
                className="w-full"
            ),
            dmc.Paper(
                dcc.Graph(id="news-chart")
            )
        ]),

        dmc.Button(tl["button"]["generate"], id="generate-news", color="dark", size="md"),
        html.Div([
            # Display a graph with the news timestamp
        ], id="news-notification-container"),
        
    ], className="flex flex-col gap-8 w-full")
