from dash import html, dcc
import dash

from tradesim.Locales import translations as tls
from tradesim.Components.ui.select import select_locale


# Layout of the home page
def main_layout(lang="fr"):
    return html.Div([
        dcc.Interval(
            id='home-clock',
            interval=5000,  # in milliseconds
        ),

        # Dropdown to change the language
        select_locale(lang, "/"),

        html.H1(tls[lang]['welcome']),
        html.P(tls[lang]['info_txt']),
        html.P(
            tls[lang]['signature'],
            className="signature"
        ),

        html.P(
            tls[lang]['button-start-info'],
            style={'display': 'none'},
            id='home-start-button-info'
        ),
        dcc.Link(
            tls[lang]['button-start'],
            href=f'/dashboard?lang={lang}',
            id='home-start-button'
        ),

        dcc.Link(
            tls[lang]['button-settings'],
            href=f'/settings?lang={lang}',
        ),

        html.Br(),
        html.Button(tls[lang]['button-restart-sim'], id='restart_sim'),

    ], className="home-container")
