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
                    id="input-mode",
                    label=tls[lang]["news-settings"]["mode"],
                    children=[
                        dmc.Radio(value="random", label=tls[lang]["news-settings"]["random-mode"]),
                        dmc.Radio(value="linear", label=tls[lang]["news-settings"]["linear-mode"]),
                    ],
                    value="random",
                ),
            ], className="flex w-full"),

            # TODO : Add a section for the number of news only in random mode
        ]),
    ], className="flex flex-col gap-8 w-full")
