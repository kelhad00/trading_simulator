from dash import html
import dash_mantine_components as dmc

from trade.components.sections import section
from trade.components.upload import upload_button


def import_settings_layout(lang="fr"):
    return html.Div([
        section("Charts", [
            upload_button(id="upload-charts", accept=".csv"),
        ]),
        section("News", [
            upload_button(id="upload-news", accept=".csv"),
        ]),
        section("Revenues", [
            upload_button(id="upload-revenues", accept=".csv"),
        ]),
    ], className="flex flex-col gap-8 w-full")
