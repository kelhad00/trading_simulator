from dash import html, dcc, page_registry
import dash_mantine_components as dmc

from trade.Locales import translations as tls
from trade.defaults import defaults as dlt

options = {**dlt.companies, **dlt.indexes}

def generate_charts(lang="fr"):
    return html.Div([
        modal(lang=lang),
        section(tls[lang]["settings-subtitles"]["charts-patterns"], [
            dmc.Select(
                id="select-company",
                label=tls[lang]["settings-number-inputs"]["number-patterns"],
                value=list(dlt.companies.keys())[0],
                data=[{"label": v, "value": k} for k, v in options.items()],
                radius="md",
                className="w-full"
            )
        ]),
        section(tls[lang]["settings-subtitles"]["final-charts"], [
            dmc.Paper(
                dcc.Graph(
                    id="final-chart",
                ),
                p="xs",
                radius="md",
                withBorder=True,
            )
        ], action_id="modify-button", action="Modify"),
    ], className="flex flex-col gap-8 w-full")




def modal(lang="fr"):
    return dmc.Modal(
        id="modal",
        title=dmc.Title("Modify Market Data", order=2, className="font-bold w-full max-w-2xl"),
        overflow="outside",
        className="flex flex-col gap-8",
        padding="xl",
        size="xl",
        radius="md",
        zIndex=10000,
        children=[
            html.Div([
                section(tls[lang]["settings-subtitles"]["market-data"], [
                    slider(tls[lang]["settings-sliders"]["alpha"], "slider-alpha", 0, 2000, 500),
                    slider(tls[lang]["settings-sliders"]["length"], "slider-length", 0, 500, 100),
                    slider(tls[lang]["settings-sliders"]["length"], "slider-start", 0, 1000, 250)
                ]),

                section(tls[lang]["settings-subtitles"]["charts-trends"], [
                    dmc.NumberInput(
                        id="number-trends",
                        label=tls[lang]["settings-number-inputs"]["number-trends"],
                        min=1,
                        max=5,
                        value=2,
                        step=1,
                        radius="md",
                        className="w-full"
                    ),
                    timeline('timeline', 2)
                ]),
                section(tls[lang]["settings-subtitles"]["final-charts"], [
                    dmc.Paper(
                        dcc.Graph(
                            id="modify-final-chart",
                        ),
                        p="xs",
                        radius="md",
                        withBorder=True,
                    )
                ]),
                dmc.Button("Modify", id="generate-button", color="dark", size="md", radius="md"),
            ], className="flex flex-col gap-8 w-full"),
        ],
    )



def timeline_item(id, index, title):
    label = tls[page_registry["lang"]]["settings-radio"]["trend"]
    options = tls[page_registry["lang"]]["settings-radio"]["options"]
    return dmc.TimelineItem(
        title=title,
        children=[
            dmc.RadioGroup(
                [dmc.Radio(l, value=k, color="dark") for k, l in
                 [("bull", options[0]), ("bear", options[1]), ("flat", options[2])]],
                label=label,
                id={"type": f"{id}-radio", "index": index},
                # orientation="vertical",
                # value="bull",
                size="sm",
            ),
        ],
        className="pb-4"
    )


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[((n // 10 % 10 != 1) * (n % 10 < 4) * n % 10)::4])

def timeline(id, nb=5):
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
                title=f"{ordinal(i)} market movement"
            ) for i in range(1, nb + 1)],
        ]
    )



def section(title, children, action=None, action_id=None):
    return html.Div([
        html.Div([
            dmc.Text(title, weight=700, className="text-[rgb(73,80,87)]", size="xl"),
            dmc.Button(action, id=action_id, color="dark", size="sm", radius="md", variant="outline") if action else None
        ], className="flex justify-between items-center w-full"),
        *children
    ], className="flex flex-col w-full gap-4 max-w-2xl")


def slider(title, id, min, max, value):
    return html.Div([
        dmc.Text(title, weight=500,
                 className="text-[rgb(73,80,87)] text-ellipsis leading-none", size="sm"),
        dmc.Slider(
            id=id,
            value=value,
            max=max,
            min=min,
            color="dark",
            # labelAlwaysOn=True,
            marks=[
                {"value": min, "label": str(min)},
                {"value": min + (max - min) // 2, "label": str(min + (max - min) // 2)},
                {"value": max, "label": str(max)},
            ],
            className="mb-4"
        ),
    ], className="flex flex-col gap-2 w-full")