from dash import html
import dash_mantine_components as dmc

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