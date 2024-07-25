from dash import html
import dash_mantine_components as dmc

def section(title, children, action=None, action_id=None):
    return html.Div([
        html.Div([
            dmc.Text(title, weight=700, className="text-[rgb(73,80,87)]", size="xl"),
            dmc.Button(action, id=action_id, color="dark", size="sm",  variant="outline") if action else None
        ], className="flex justify-between items-center w-full"),
        *children
    ], className="flex flex-col w-full gap-4 max-w-2xl")
