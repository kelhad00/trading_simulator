from dash import html, dcc
import dash
import dash_mantine_components as dmc

from tradesim.Locales import translations as tls

# Layout of the home page
def main_layout(lang="fr"):
    return html.Div([
        html.H1("Market data creation"),
        dmc.Slider(
            id="slider-callback",
            value=100,
            min=0,
            max=600,
            style={"width": "300px"}
        ),
        # dmc.Slider(
        #     label="Select length",
        #     min=0,
        #     max=600,
        #     step=1,
        # ),

        html.H1("Test Page"),
        html.P("This is a test page.")
    ])