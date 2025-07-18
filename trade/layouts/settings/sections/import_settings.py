from dash import html
import dash_mantine_components as dmc

from trade.components.sections import section
from trade.components.upload import upload_button

from trade.locales import translations as tls


def import_settings_layout(lang="fr"):
    return html.Div([
        section(tls[lang]["settings"]["tabs"]["chart"]+" (.csv)", [
            upload_button(id="upload-charts", accept=".csv"),
        ]),
        section(tls[lang]["settings"]["tabs"]["news"]+" (.csv)", [
            upload_button(id="upload-news", accept=".csv"),
        ]),
        section(tls[lang]["settings"]["tabs"]["revenues"]+" (.csv)", [
            upload_button(id="upload-revenues", accept=".csv"),
        ]),
        html.P([
            "Voici un lien vers " if lang == "fr" else "Link to the ",
            html.A("Wiki", href="https://github.com/kelhad00/trading_simulator/blob/main/WIKI_FR.md" if lang == "fr" else "https://github.com/kelhad00/trading_simulator/blob/main/WIKI.md", target="_blank"),]
        ),
    ], className="flex flex-col gap-8 w-full items-center")
