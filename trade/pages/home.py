import dash
from dash import html, dcc, Input, Output, callback
from dash.exceptions import PreventUpdate

from trade.Locales import translations as tls

from trade.layouts import home

from trade.components import menu


dash.register_page(
    __name__,
	path="/",
)

def layout(lang="fr", **kwargs):
	dash.page_registry['lang'] = lang
	return home.main_layout(lang)


