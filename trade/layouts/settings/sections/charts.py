from dash import html, dcc, page_registry
import dash_mantine_components as dmc

from trade.components.modal import modal
from trade.components.radio import radio
from trade.components.sections import section
from trade.components.slider import slider
from trade.locales import translations as tls
from trade.utils.ordinal import ordinal


button_labels = [
    'Very Bull',
    'Medium Bull',
    'Small Bull',
    'Flat',
    'Small Bear',
    'Medium Bear',
    'Very Bear'
]

def bull_buttons(lang = "fr", pattern_type="with"):
    tl = tls[lang]["settings"]["charts"]["button"]
    return [dmc.Button(
            tl[label],
            id={'type': 'add-button', 'index': label, 'pattern_type': pattern_type},
            n_clicks=0,
            color="green",
            size="sm",
            className="m-1"
        ) for label in button_labels if 'Bull' in label
    ]

def flat_buttons(lang = "fr", pattern_type="with"):
    tl = tls[lang]["settings"]["charts"]["button"]
    return [dmc.Button(
            tl[label],
            id={'type': 'add-button', 'index': label, 'pattern_type': pattern_type},
            n_clicks=0,
            color="gray",
            size="sm",
            className="m-1"
        ) for label in button_labels if 'Flat' in label
    ]

def bear_buttons(lang = "fr", pattern_type="with"):
    tl = tls[lang]["settings"]["charts"]["button"]
    return  [dmc.Button(
            tl[label],
            id={'type': 'add-button', 'index': label, 'pattern_type': pattern_type},
            n_clicks=0,
            color="red",
            size="sm",
            className="m-1"
        ) for label in button_labels if 'Bear' in label
    ]

def pattern_section(title, lang="fr", pattern_type="with"):
    return html.Div([
        dmc.Text(title, size="md", weight=700, className="mb-2 mt-2"),
        layout(lang=lang, pattern_type=pattern_type)
    ], className="mb-4")

# On adapte layout pour accepter pattern_type ("with" ou "without")
def layout(lang = "fr", pattern_type="with"):
    label = "Avec pattern" if pattern_type == "with" else "Sans pattern"
    return html.Div([
        html.Div([
            html.Div(bull_buttons(lang, pattern_type), style={'display': 'flex', 'flexDirection': 'row'})
        ], className="mb-2"),
        html.Div([
             html.Div(flat_buttons(lang, pattern_type), style={'display': 'flex', 'flexDirection': 'row'})
        ], className="mb-2") if pattern_type != "with" else None,
        html.Div([
            html.Div(bear_buttons(lang, pattern_type), style={'display': 'flex', 'flexDirection': 'row'})
        ], className="mb-2"),
    ], style={'display': 'flex', 'flexDirection': 'column'}, id={"type": "pattern-section", "pattern_type": pattern_type})

# On adapte editor pour afficher les deux sections

def editor(lang = "fr"):
    tl = tls[lang]["settings"]["charts"]
    # Liste d'exemple de patterns (à remplacer par la vraie liste plus tard)
    return html.Div([
        pattern_section(tl["subtitles"].get("with_pattern", "Avec pattern"), lang, pattern_type="with"),
        pattern_section(tl["subtitles"].get("without_pattern", "Sans pattern"), lang, pattern_type="without"),

        # Bloc selecteur de pattern + bouton ajouter
        html.Div([
            dmc.Text("Pattern", size="md", weight=700, className="mb-2 mt-2"),
            html.Br(),
            dmc.Select(
                id="pattern-selector",
                data=[
                    {"value": "double_top", "label": tl["patterns_names"]["double_top"]},
                    {"value": "head_and_shoulders", "label": tl["patterns_names"]["head_and_shoulders"]},
                    {"value": "double_bottom", "label": tl["patterns_names"]["double_bottom"]},
                    {"value": "inverse_head_and_shoulders", "label": tl["patterns_names"]["inverse_head_and_shoulders"]},
                ],
                className="mb-2 w-60",
                value="bullish_engulfing"
            ),
            dmc.Button(
                tl["button"]["add_pattern"],
                id="add-pattern-button",
                color="dark",
                size="sm",
                className="ml-2"
            )
        ], className="flex flex-row items-end mb-2 gap-2 items-center"),


        html.Div([
            dmc.Text(tl["select"].get("granularity", "Granularité :"), size="sm", weight=500, className="mb-1"),
            dmc.Select(
                id="granularity-select",
                data=[
                    {"value": "ME", "label": tl["select"]["month"]},
                    {"value": "W", "label": tl["select"]["week"]},
                    {"value": "D", "label": tl["select"]["day"]},
                    {"value": "h", "label": tl["select"]["hour"]},
                ],
                value="D",
                className="mb-2 w-40"
            ),
            dmc.Text(tl["select"].get("date_range", "Période de génération :"), size="sm", weight=500, className="mb-1"),
            dcc.DatePickerRange(
                id="date-picker-range",
                display_format="YYYY-MM-DD",
                start_date_placeholder_text=tl["select"].get("start_date", "Date de début"),
                end_date_placeholder_text=tl["select"].get("end_date", "Date de fin"),
                className="mb-4"
            )
        ], className="flex flex-col gap-2 w-full"),

        html.Br(),

        html.Div(id='timeline', style={'display': 'flex', 'flexDirection': 'row', 'overflowX': 'auto', 'whiteSpace': 'nowrap'}),

        dmc.Button(
            tl["button"]["refresh"],
            id='refresh-button',
            n_clicks=0,
            color="dark",
            size="sm",
            variant="outline"
        ),

        section(tl["subtitles"]["preview"], [
            dmc.Paper(
                html.Div(id="chart_new")
            )
        ]),

        dmc.Button(
            tl["button"]["modify"],
            id='modify-button-new-graph',
            n_clicks=0,
            color="dark",
            size="sm"
        ),

        dcc.Store(id="size-store", data={}, storage_type="session"),

    ], className="flex flex-col gap-8 w-full")


def generate_charts(lang="fr"):
    tl = tls[lang]["settings"]["charts"]
    return html.Div([
        dcc.Store(id="figures"),
        dcc.Store(id="new-graph-df"),
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
        ]),

    ], className="flex flex-col gap-8 w-full items-center")


def generate_chars_selection(lang="fr"):
    tl = tls[lang]["settings"]["charts"]
    return html.Div([
        dmc.Tabs(
            [
                dmc.TabsList([
                    dmc.Tab(tl["subtitles"]["Old generator"],value="old"),
                    dmc.Tab(tl["subtitles"]["New generator"],value="new")
                ],grow=True),

                dmc.TabsPanel(generate_charts(lang=lang),value="old"),
                dmc.TabsPanel(editor(lang=lang),value="new"),
            ],
            value="old",
            id="generation-charts-tab",
            color="dark",
            radius="md",
            className="w-full flex flex-col gap-8"
        )
    ])

def generate_charts_modal(lang="fr"):
    tl = tls[lang]["settings"]["charts"]
    return modal(
        id="modal",
        title=tl["subtitles"]["modal"],
        children=[
            html.Div([
                section(tl["subtitles"]["ticker"], [
                    html.Div([
                        dmc.Select(
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
                        html.Div(
                            dcc.Graph(),
                            id="modal-generated-charts-container",
                        ),
                    )
                ]),
                dmc.Button(tl["button"]["modify"], id="generate-button", color="dark", size="md", ),
            ], className="flex flex-col gap-8 w-full"),
        ]
    )



def timeline_item(id, index, title):
    label = tls[page_registry["lang"]]["settings"]["charts"]["radio"]["label"]
    option_values = tls[page_registry["lang"]]["settings"]["charts"]["radio"]["options"]

    options = [("bull", option_values[0]), ("bear", option_values[1])]

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







