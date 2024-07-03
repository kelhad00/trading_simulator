from dash import html, dcc
import dash

from tradesim.Layouts import home
from tradesim.Locales import translations as tls


dash.register_page(
    __name__,
    path='/',
)



def layout(lang="fr", **kwargs):
    from tradesim.app import app # Import here to avoid circular import
    app.dashboardIsRunning = False # Disable the dashboard
    print("home layout")

    if lang not in tls.keys(): lang = "fr" # Handle invalid language
    dash.page_registry['lang'] = lang      # Provide the language to the callbacks

    return home.main_layout(lang) # Import the layout with the selected language


# Import callbacks
from tradesim.Components import home as callbacks