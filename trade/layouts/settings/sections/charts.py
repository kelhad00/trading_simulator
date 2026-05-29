from dash import html, dcc, page_registry
import dash_mantine_components as dmc

from trade.components.modal import modal
from trade.components.radio import radio
from trade.components.sections import section
from trade.components.slider import slider
from trade.locales import translations as tls
from trade.utils.ordinal import ordinal


def generate_charts(lang="fr"):
    tl = tls[lang]["settings"]["charts"]
    return html.Div([
        dcc.Store(id="figures"),        # final data exported to CSV on confirm
        dcc.Store(id="base-figures"),   # CAC40 window indices, fixed until trends change
        dcc.Store(id="pattern-files"),  # chosen pattern CSV paths, fixed until patterns change
        generate_charts_modal(lang=lang),
        section(tl["subtitles"]["ticker"], [
            dmc.Select(
                id="select-company",
                label=tl["select"]["ticker"],
                className="w-full"
            )
        ]),
        section(tl["subtitles"]["preview"], [
            dmc.Paper(
                dcc.Graph(id="chart")
            )
        ], action_id="modify-button", action=tl["button"]["modify"]),

        dmc.Button(tl["button"]["delete"], id="button-delete-charts", color="dark"),

    ], className="flex flex-col gap-8 w-full")




def generate_charts_modal(lang="fr"):
    tl = tls[lang]["settings"]["charts"]
    return modal(
        id="modal",
        title=tl["subtitles"]["modal"],
        children=[
            html.Div([
                section(tl["subtitles"]["ticker"], [
                    html.Div([
                        dmc.MultiSelect(
                            id="modal-select-companies",
                            label=tl["select"]["ticker"],
                            className="flex-1"
                        ),
                        dmc.Button(tl["button"]["select-all"], id="select-all-stocks", color="dark", size="sm"),
                    ], className="flex gap-4 w-full items-end")
                ]),

                section(tl["subtitles"]["parameters"], [
                    html.Div(
                        slider(tl["select"]["alpha"], "slider-alpha", 0, 2000, 500),
                        id="alpha-section",
                    ),
                    slider(tl["select"]["start"], "slider-start", 0, 1000, 250)
                ]),

                section(tl["subtitles"]["trends"], [
                    dmc.NumberInput(
                        id="number-trends",
                        label=tl["input"]["trends"],
                        min=1, max=5, value=2, step=1,
                        className="w-full"
                    ),
                    html.Div(
                        timeline('timeline', 2),
                        id="timeline-radio-section",
                    ),
                ]),

                section(tl["event"]["title"], [
                    dmc.Select(
                        id="select-event-type",
                        label=tl["event"]["type-label"],
                        data=[
                            {"label": tl["event"]["none"],  "value": "none"},
                            {"label": tl["event"]["crash"], "value": "crash"},
                            {"label": tl["event"]["rally"], "value": "rally"},
                        ],
                        value="none",
                        className="w-full",
                    ),
                    html.Div(
                        id="event-params-container",
                        style={"display": "none"},
                        children=[
                            slider(tl["event"]["position"], "slider-event-position", 0, 100, 50),
                            slider(tl["event"]["magnitude"], "slider-event-magnitude", 5, 80, 40),
                        ],
                    ),
                    dmc.Alert(
                        id="event-overlap-warning",
                        color="yellow",
                        style={"display": "none"},
                    ),
                ]),

                section(tl["subtitles"]["preview"], [
                    dmc.Text(
                        id="chart-bar-count",
                        size="sm",
                        color="dimmed",
                    ),
                    dmc.Paper(
                        html.Div(dcc.Graph(), id="modal-generated-charts-container"),
                    )
                ]),
                dmc.Button(tl["button"]["modify"], id="generate-button", color="dark", size="md", ),
            ], className="flex flex-col gap-8 w-full"),
        ]
    )



def timeline_item(id, index, title, lang=None):
    lang = lang or page_registry["lang"]
    tl = tls[lang]["settings"]["charts"]
    label = tl["radio"]["label"]
    option_values = tl["radio"]["options"]
    pattern_tl = tl["pattern-select"]

    options = [("bull", option_values[0]), ("bear", option_values[1]), ("flat", option_values[2])]

    pattern_options = [
        {"label": pattern_tl["none"],                       "value": "none"},
        {"label": pattern_tl["double_top"],                 "value": "double_top"},
        {"label": pattern_tl["double_bottom"],              "value": "double_bottom"},
        {"label": pattern_tl["head_and_shoulders"],         "value": "head_and_shoulders"},
        {"label": pattern_tl["inverse_head_and_shoulders"], "value": "inverse_head_and_shoulders"},
        {"label": pattern_tl["ascending_triangle"],         "value": "ascending_triangle"},
        {"label": pattern_tl["descending_triangle"],        "value": "descending_triangle"},
        {"label": pattern_tl["bullish_flag"],               "value": "bullish_flag"},
        {"label": pattern_tl["bearish_flag"],               "value": "bearish_flag"},
        {"label": pattern_tl["cup_and_handle"],             "value": "cup_and_handle"},
        {"label": pattern_tl["rising_wedge"],               "value": "rising_wedge"},
        {"label": pattern_tl["falling_wedge"],              "value": "falling_wedge"},
    ]

    return dmc.TimelineItem(
        title=title,
        children=[
            html.Div(
                radio(options, label, {"type": f"{id}-radio", "index": index}),
                id={"type": f"{id}-radio-container", "index": index},
            ),
            dmc.Select(
                id={"type": f"{id}-pattern", "index": index},
                label=pattern_tl["label"],
                data=pattern_options,
                value="none",
                size="sm",
                className="w-full mt-2",
            ),
            dmc.Text(
                id={"type": f"{id}-pattern-quality", "index": index},
                size="xs",
                color="dimmed",
                className="mt-1",
            ),
            html.Div(
                slider(tl["select"]["segment-length"], {"type": f"{id}-length", "index": index}, 10, 500, 100),
                id={"type": f"{id}-length-container", "index": index},
                className="mt-2",
            ),
        ],
        className="pb-4"
    )




def timeline(id, nb=5):
    def format_title(i):
        lang = page_registry["lang"]
        title = tls[lang]["settings"]["charts"]["radio"]["title"]
        return f"{ordinal(i, lang)} {title}"

    return dmc.Timeline(
        id=id,
        active=2,
        bulletSize=15,
        lineWidth=4,
        color="dark",
        children=[
            *[timeline_item(
                id=id,
                index=i,
                title=format_title(i)
            ) for i in range(1, nb + 1)],
        ]
    )
