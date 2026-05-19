from dash import html, dcc, page_registry
import dash_mantine_components as dmc

from trade.components.modal import modal
from trade.components.radio import radio
from trade.components.sections import section
from trade.components.slider import slider
from trade.locales import translations as tls
from trade.defaults import defaults as dlt
from trade.utils.ordinal import ordinal


def generate_charts(lang="fr"):
    tl = tls[lang]["settings"]["charts"]
    return html.Div([
        dcc.Store(id="figures"),  # Store the generated data before being stored in the csv file
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
                    slider(tl["select"]["alpha"], "slider-alpha", 0, 2000, 500),
                    slider(tl["select"]["length"], "slider-length", 0, 500, 100),
                    slider(tl["select"]["start"], "slider-start", 0, 1000, 250)
                ]),

                section(tl["subtitles"]["trends"], [
                    dmc.NumberInput(
                        id="number-trends",
                        label=tl["input"]["trends"],
                        min=1, max=5, value=2, step=1,
                        className="w-full"
                    ),
                    timeline('timeline', 2)
                ]),

                section(tl["subtitles"]["preview"], [
                    dmc.Paper(
                        html.Div(dcc.Graph(), id="modal-generated-charts-container"),
                    )
                ]),
                dmc.Button(tl["button"]["modify"], id="generate-button", color="dark", size="md", ),
            ], className="flex flex-col gap-8 w-full"),
        ]
    )



def timeline_item(id, index, title):
    label = tls[page_registry["lang"]]["settings"]["charts"]["radio"]["label"]
    option_values = tls[page_registry["lang"]]["settings"]["charts"]["radio"]["options"]

    options = [("bull", option_values[0]), ("bear", option_values[1]), ("flat", option_values[2])]

    return dmc.TimelineItem(
        title=title,
        children=[
            radio(options, label, {"type": f"{id}-radio", "index": index}),
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







