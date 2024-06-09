from dash import html, dcc
import dash

from tradesim.Locales import translations as tls


def select_locale(lang, url="/"):
    print("select_locale")
    return html.Div([
        html.Button([
            html.Span(lang),
            html.Span(className="arrow")
        ]),
        html.Ul([
            html.Li(
                dcc.Link(l, href=f'{url}?lang={l}')
            ) for l in tls.keys() if l != lang
        ])
    ],
        className="switch-lang-btn"
    )