import dash
from trade.layouts.settings.layout import main_layout

# Don't delete this import
from trade.callbacks.settings import settings, stocks, advanced

dash.register_page(__name__, path="/settings",)


def layout(lang="fr", **kwargs):
    dash.page_registry['lang'] = lang
    return main_layout(lang)