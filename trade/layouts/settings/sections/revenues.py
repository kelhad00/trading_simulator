from dash import html, dcc
import dash_mantine_components as dmc

from trade.components.modal import modal
from trade.components.radio import radio
from trade.components.sections import section
from trade.locales import translations as tls

def revenues_layout(lang="fr"):
    tl = tls[lang]["settings"]["revenues"]
    return html.Div([
        dcc.Store(id="revenues"),
        generate_revenues_modal(lang),

        section(tl["subtitles"]["ticker"], [
            html.Div([
                dmc.MultiSelect(
                    id="select-companies-revenues",
                    label=tl["select"]["ticker"],
                    className="flex-1"
                ),
                dmc.Button(tl["button"]["select-all"], id="select-all-companies-revenues", color="dark", size="sm"),
            ], className="flex gap-4 w-full items-end"),
        ]),

        section(tl["subtitles"]["preview"],
                [dmc.Paper(
                    html.Div(dcc.Graph(), id="revenues-container")
                )],
            action_id="button-modify-revenues",
            action=tl["button"]["modify"]
        ),

        dmc.Button(tl["button"]["delete"], id="button-delete-revenues", color="dark"),

    ], className="flex flex-col gap-8 w-full")



def generate_revenues_modal(lang="fr"):
    tl = tls[lang]["settings"]["revenues"]
    return modal(
        id="modal-revenues",
        title=tl["subtitles"]["modal"],
        children=[
            html.Div([

                section(tl["subtitles"]["ticker"], [
                    html.Div([
                        dmc.MultiSelect(
                            id="modal-select-companies-revenues",
                            label=tl["select"]["ticker"],
                            className="flex-1"
                        ),
                        dmc.Button(tl["button"]["select-all"], id="modal-select-all-companies-revenues",
                                   color="dark", size="sm"),
                    ], className="flex gap-4 w-full items-end"),
                ]),

                section(tl["subtitles"]["mode"], [
                    radio(
                        options=[("auto", tl["radio"]["options"][0]), ("manual", tl["radio"]["options"][1])],
                        label=tl["radio"]["label"],
                        value="auto",
                        id="modal-radio-mode-revenues",
                    ),
                ]),

                section(
                    title=tl["subtitles"]["form"],
                    children=[html.Div(
                        id="modal-input-container-revenues",
                        className="flex flex-col gap-4 w-full"
                    )]
                ),
                dmc.Button(tl["button"]["confirm"], id="generate-revenues", color="dark", size="md"),
            ], className="flex flex-col gap-8 w-full"),
        ]
    )

