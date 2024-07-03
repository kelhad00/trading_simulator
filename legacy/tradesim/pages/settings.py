import dash
from dash import html

from tradesim.Layouts import settings
from tradesim.Locales import translations as tls


dash.register_page(
    __name__,
    path='/settings',
)

def layout(lang="fr", **kwargs):
    from tradesim.app import app # Import here to avoid circular import
    app.dashboardIsRunning = False # Disable the dashboard

    if lang not in tls.keys(): lang = "fr" # Handle invalid language
    dash.page_registry['lang'] = lang      # Provide the language to the callbacks

    return settings.main_layout(lang) # Import the layout with the selected language
