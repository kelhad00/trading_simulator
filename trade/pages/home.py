import dash
from trade.layouts import home

# Don't delete these imports — they register callbacks as side-effects
from trade.callbacks import reset
from trade.callbacks import home as home_callbacks  # noqa: F401

dash.register_page(__name__, path="/")


def layout(lang="fr", **kwargs):
	dash.page_registry['lang'] = lang
	return home.main_layout(lang)


