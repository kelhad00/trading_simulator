import dash

from emotrade.Layouts import dashboard
from emotrade.Locales import translations as tls


dash.register_page(
    __name__,
    path='/',
    path_template="/<lang>/",
)


def layout(lang="fr"):
    # Import callbacks
    # This is done after app initialization to avoid circular imports.
    from emotrade.States import import_data, save_state
    from emotrade.Components import graph, portfolio, requests, news

    if lang not in tls.keys(): lang = "fr" # Handle invalid language
    dash.page_registry['lang'] = lang      # Provide the language to the callbacks

    return dashboard.main_layout(lang) # Import the layout with the selected language

