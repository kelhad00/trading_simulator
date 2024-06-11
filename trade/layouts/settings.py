from dash import html, dcc, callback, Output, Input, callback_context, no_update
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from trade.layouts.shared import header


def main_layout(lang="fr"):
    return html.Div([
        header(lang, url="/settings"),
        dmc.Title("Settings", order=1, className="font-bold leading-none w-full max-w-2xl"),

        section("Market data creation", [
            slider("Select alpha value", "slider-alpha", 0, 2000, 500),
            slider("Select length value", "slider-length", 0, 500, 100)
        ]),

        section("Charts trends", [
            dmc.NumberInput(
                id="number-trends",
                label="Number of charts trends",
                min=1,
                max=5,
                value=2,
                step=1,
                radius="md",
                className="w-full"
            ),
            timeline('timeline', 2)
        ]),

        section("Charts patterns", [
            dmc.NumberInput(
                id="number-patterns",
                label="Number of patterns",
                min=0,
                max=4,
                value=0,
                step=1,
                radius="md",
                className="w-full"
            )
        ]),

        section("Final charts", [
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
    return dmc.TimelineItem(
        title=title,
        children=[
            dmc.RadioGroup(
                [dmc.Radio(l, value=k, color="dark") for k, l in
                 [("bull", "Bull 📈"), ("bear", "Bear 📉"), ("flat", "Flat")]],
                label="Select an option" + str(id),
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