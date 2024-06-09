import dash
from dash import html, dcc

from trade.Locales import translations as tls



dash.register_page(
    __name__,
    path="/settings",
)

def layout(lang="fr", **kwargs):
    dash.page_registry['lang'] = lang

    return html.Span("Settings")