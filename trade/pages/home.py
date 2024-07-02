import dash
from trade.layouts import home

# Don't delete this import
from trade.callbacks import reset

dash.register_page(__name__, path="/")


def layout(lang="fr", **kwargs):
	dash.page_registry['lang'] = lang
	return home.main_layout(lang)


