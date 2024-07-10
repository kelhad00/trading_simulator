from dash import html
import dash_mantine_components as dmc

from trade.components.sections import section
from trade.locales import translations as tls


def news_settings(lang="fr"):
    return html.Div([
        section(tls[lang]["settings-subtitles"]["api"], [
            html.Div([
                dmc.TextInput(
                    id="input-api-key",
                    label=tls[lang]["settings-api"],
                    className="flex-1",
                    value="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", # TODO: REMOVE IT
                ),
            ], className="flex w-full"),
        ]),
        section(tls[lang]["settings-subtitles"]["news-generation-param"], [
            html.Div([
                dmc.NumberInput(
                    id="input-alpha",
                    label=tls[lang]["news-settings"]["alpha"],
                    className="flex-1",
                    value=3,
                ),
            ], className="flex w-full"),

            html.Div([
                dmc.NumberInput(
                    id="input-alpha-day-interval",
                    label=tls[lang]["news-settings"]["alpha-day-interval"],
                    className="flex-1",
                    value=3,
                ),
            ], className="flex w-full"),

            html.Div([
                dmc.NumberInput(
                    id="input-delta",
                    label=tls[lang]["news-settings"]["delta"],
                    className="flex-1",
                    value=0,
                ),
            ], className="flex w-full"),

            html.Div([
                dmc.RadioGroup(
                    id="input-generation-mode",
                    label=tls[lang]["news-settings"]["mode"],
                    children=[
                        dmc.Radio(value="random", label=tls[lang]["news-settings"]["random-mode"]),
                        dmc.Radio(value="linear", label=tls[lang]["news-settings"]["linear-mode"]),
                    ],
                    value="random",
                ),
            ], className="flex w-full"),

            # Display the number of news input only in random mode
            html.Div([
                dmc.NumberInput(
                    id="input-nbr-positive-news",
                    label=tls[lang]["news-settings"]["nbr-positive-news"],
                    className="flex-1",
                    value=5,
                ),
                dmc.NumberInput(
                    id="input-nbr-negative-news",
                    label=tls[lang]["news-settings"]["nbr-negative-news"],
                    className="flex-1",
                    value=5,
                ),
            ], className="flex w-full", id="nbr-news-container"),

            dmc.Button(tls[lang]["settings-button"]["modify"], id="modify-news", color="dark", size="md"),

            dmc.Button(tls[lang]["settings-button"]["generate"], id="generate-news", color="dark", size="md"),

            html.Div([
                # Display a graph with the news timestamp
            ], id="news-notification-container"),
        ]),
    ], className="flex flex-col gap-8 w-full")
