import dash
from trade.layouts.dashboard.layout import main_layout

# Don't delete this import
from trade.callbacks.dashboard import news, portfolio, graph, request, export

dash.register_page(__name__, path="/dashboard")


def layout(lang="fr", **kwargs):
    dash.page_registry['lang'] = lang
    return main_layout(lang)




