from dash import html, dcc, page_registry
import dash_mantine_components as dmc

from trade.components.modal import modal
from trade.components.radio import radio
from trade.components.sections import section
from trade.components.slider import slider
from trade.locales import translations as tls
from trade.defaults import defaults as dlt
from trade.utils.ordinal import ordinal

options = {**dlt.companies, **dlt.indexes}

def generate_charts(lang="fr"):
    return html.Div([
        dcc.Store(id="figures"),  # Store the generated data before being stored in the csv file
        generate_charts_modal(lang=lang),
        section(tls[lang]["settings-subtitles"]["charts-patterns"], [
            dmc.Select(
                id="select-company",
                label=tls[lang]["settings-number-inputs"]["number-patterns"],
                className="w-full"
            )
        ]),
        section(tls[lang]["settings-subtitles"]["final-charts"], [
            dmc.Paper(
                dcc.Graph(id="chart")
            )
        ], action_id="modify-button", action=tls[lang]["settings-button"]["modify"]),

        dmc.Button("Delete", id="button-delete-charts", color="dark"),

    ], className="flex flex-col gap-8 w-full")




def generate_charts_modal(lang="fr"):
    return modal(
        id="modal",
        title=tls[lang]["settings-subtitles"]["generate-modal"],
        children=[
            html.Div([
                section(tls[lang]["settings-subtitles"]["charts-patterns"], [
                    html.Div([
                        dmc.MultiSelect(
                            id="modal-select-companies",
                            label=tls[lang]["settings-number-inputs"]["number-patterns"],
                            className="flex-1"
                        ),
                        dmc.Button(tls[lang]["settings-button"]["select-all"], id="select-all-stocks", color="dark", size="sm"),
                    ], className="flex gap-4 w-full items-end")
                ]),

                section(tls[lang]["settings-subtitles"]["market-data"], [
                    slider(tls[lang]["settings-sliders"]["alpha"], "slider-alpha", 0, 2000, 500),
                    slider(tls[lang]["settings-sliders"]["length"], "slider-length", 0, 500, 100),
                    slider("Selectionner la valeur de départ", "slider-start", 0, 1000, 250)
                ]),

                section(tls[lang]["settings-subtitles"]["charts-trends"], [
                    dmc.NumberInput(
                        id="number-trends",
                        label=tls[lang]["settings-number-inputs"]["number-trends"],
                        min=1, max=5, value=2, step=1,
                        className="w-full"
                    ),
                    timeline('timeline', 2)
                ]),

                section(tls[lang]["settings-subtitles"]["final-charts"], [
                    dmc.Paper(
                        html.Div(dcc.Graph(), id="modal-generated-charts-container"),
                    )
                ]),
                dmc.Button(tls[lang]["settings-button"]["modify"], id="generate-button", color="dark", size="md", ),
            ], className="flex flex-col gap-8 w-full"),
        ]
    )



def timeline_item(id, index, title):
    label = tls[page_registry["lang"]]["settings-radio"]["trend"]
    option_values = tls[page_registry["lang"]]["settings-radio"]["options"]

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
        title = tls[lang]["settings-timeline"]
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







