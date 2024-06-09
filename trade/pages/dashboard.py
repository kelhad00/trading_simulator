import dash
from trade.layouts import dashboard

# Callbacks
from trade.components import portfolio, graph, news, request, menu


dash.register_page(
    __name__,
    path="/dashboard",
)


def layout(lang="fr", **kwargs):
    dash.page_registry['lang'] = lang
    return dashboard.main_layout(lang)




