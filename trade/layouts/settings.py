from dash import html, dcc, callback, Output, Input, callback_context, no_update, page_registry
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from trade.layouts.shared import header

from trade.Locales import translations as tls


def main_layout(lang="fr"):
    return html.Div([
        header(lang, url="/settings"),
        dmc.Title(tls[lang]["settings-title"], order=1, className="font-bold leading-none w-full max-w-2xl"),

        section(tls[lang]["settings-subtitles"]["market-data"], [
            slider(tls[lang]["settings-sliders"]["alpha"], "slider-alpha", 0, 2000, 500),
            slider(tls[lang]["settings-sliders"]["length"], "slider-length", 0, 500, 100)
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

        section(tls[lang]["settings-subtitles"]["charts-patterns"], [
            dmc.NumberInput(
                id="number-patterns",
                label=tls[lang]["settings-number-inputs"]["number-patterns"],
                min=0,
                max=4,
                value=0,
                step=1,
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
        ]),
    ], className="px-12 p-8 bg-gray-100 flex flex-col items-center h-screen gap-8 overflow-auto"),




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



def section(title, children):
    return html.Div([
        dmc.Text(title, weight=700, className="text-[rgb(73,80,87)]", size="xl"),
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