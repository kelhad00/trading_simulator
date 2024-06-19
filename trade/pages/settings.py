import dash
from dash import html

from trade.callbacks import settings as callbacks, stocks as stocks_callbacks

from trade.layouts.settings import settings

dash.register_page(
    __name__,
    path="/settings",
)

def layout(lang="fr", **kwargs):
    dash.page_registry['lang'] = lang

    return settings.main_layout(lang)