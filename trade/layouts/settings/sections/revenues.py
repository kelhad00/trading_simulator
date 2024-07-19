from dash import html, dcc
import dash_mantine_components as dmc

from trade.components.modal import modal
from trade.components.radio import radio
from trade.components.sections import section
from trade.locales import translations as tls

def revenues_layout(lang="fr"):
    return html.Div([
        dcc.Store(id="revenues"),
        generate_revenues_modal(lang="fr"),

        section(tls[lang]["settings-subtitles"]["charts-patterns"], [
            html.Div([
                dmc.MultiSelect(
                    id="select-companies-revenues",
                    label=tls[lang]["settings-number-inputs"]["number-patterns"],
                    className="flex-1"
                ),
                dmc.Button(tls[lang]["settings-button"]["select-all"], id="select-all-companies-revenues", color="dark", size="sm"),
            ], className="flex gap-4 w-full items-end"),
        ]),

        section(tls[lang]["settings-subtitles"]["final-charts"],
                [dmc.Paper(
                    html.Div(dcc.Graph(), id="testo")
                )],
            action_id="button-modify-revenues",
            action=tls[lang]["settings-button"]["modify"]
        ),



    ], className="flex flex-col gap-8 w-full")



def generate_revenues_modal(lang="fr"):
    return modal(
        id="modal-revenues",
        title="generer des revenus",
        children=[
            html.Div([

                section("Choix de l'entreprise", [
                    html.Div([
                        dmc.MultiSelect(
                            id="modal-select-companies-revenues",
                            label=tls[lang]["settings-number-inputs"]["number-patterns"],
                            className="flex-1"
                        ),
                        dmc.Button(tls[lang]["settings-button"]["select-all"], id="modal-select-all-companies-revenues",
                                   color="dark", size="sm"),
                    ], className="flex gap-4 w-full items-end"),
                ]),

                section("Choix du mode", [
                    radio(
                        options=[("auto", "Auto"), ("manual", "Manual")],
                        label="Choose a mode",
                        value="auto",
                        id="modal-radio-mode-revenues",
                    ),
                ]),

                section(
                    title="Revenues",
                    children=[html.Div(
                        id="modal-input-container-revenues",
                        className="flex flex-col gap-4 w-full"
                    )]
                ),
                dmc.Button("Apply", id="generate-revenues", color="dark", size="md"),
            ], className="flex flex-col gap-8 w-full"),
        ]
    )

