from dash import html
import dash_mantine_components as dmc

from trade.components.sections import section
from trade.components.upload import upload_button

from trade.locales import translations as tls


def import_settings_layout(lang="fr"):
    return html.Div([
        section(tls[lang]["settings"]["tabs"]["chart"], [
            upload_button(id="upload-charts", accept=".csv"),
        ]),
        section(tls[lang]["settings"]["tabs"]["news"], [
            upload_button(id="upload-news", accept=".csv"),
        ]),
        section(tls[lang]["settings"]["tabs"]["revenues"], [
            upload_button(id="upload-revenues", accept=".csv"),
        ]),
    ], className="flex flex-col gap-8 w-full")
