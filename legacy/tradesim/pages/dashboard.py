import dash

from tradesim.Layouts import dashboard
from tradesim.Locales import translations as tls


dash.register_page(
    __name__,
    path='/dashboard',
)


def layout(lang="fr", **kwargs):
    from tradesim.app import app # Import here to avoid circular import
    app.dashboardIsRunning = True # Set the dashboard as running

    if lang not in tls.keys(): lang = "fr" # Handle invalid language
    dash.page_registry['lang'] = lang      # Provide the language to the callbacks

    return dashboard.main_layout(lang) # Import the layout with the selected language


# Import callbacks
from tradesim.States import import_data, save_state
from tradesim.Components import graph, portfolio, requests, news

