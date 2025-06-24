import dash_mantine_components as dmc
from dash import html, dcc

from trade.components.sections import section
from trade.locales import translations as tls


def pattern_config(lang = "fr"):
    tl = tls[lang]["settings"]["charts"]

    # Liste des patterns et labels traduits
    pattern_options = [
        {"value": "bullish_engulfing", "label": tl["patterns_names"]["bullish_engulfing"]},
        {"value": "bearish_engulfing", "label": tl["patterns_names"]["bearish_engulfing"]},
        {"value": "hammer", "label": tl["patterns_names"]["hammer"]},
        {"value": "shooting_star", "label": tl["patterns_names"]["shooting_star"]},
        {"value": "double_top", "label": tl["patterns_names"]["double_top"]},
        {"value": "head_and_shoulders", "label": tl["patterns_names"]["head_and_shoulders"]},
    ]

    return html.Div( [
        section(tl["subtitles"]["pattern_config"], [
            dmc.Select(
                id="pattern-select",
                label=tl["select"]["pattern"],
                data=pattern_options,
                className="w-full",
            ),
            html.Div(id="pattern-params-container"),
            dmc.Group([
                dmc.Button(
                    tl["button"]["save_pattern_config"],
                    id="save-pattern-config-btn",
                    color="blue",
                    className="mt-4"
                ),
                dmc.Button(
                    tl["button"]["reset_pattern_config"],
                    id="reset-pattern-config-btn",
                    color="gray",
                    className="mt-4"
                ),
            ], position="left", className="mb-2"),
            section(tl["subtitles"]["pattern_preview"], [
                dmc.Paper(
                    dcc.Graph(id="pattern-preview-graph")
                )
            ]),
            html.Div(id="save-pattern-config-msg")
        ])
    ],className="flex flex-col gap-8 w-full")