from dash import html, dcc
import dash

from tradingsimulator.Layouts import home
from tradingsimulator.Locales import translations as tls


dash.register_page(
    __name__,
    path_template="/<lang>/"
)


def layout(lang="fr"):
    from tradingsimulator.app import app # Import here to avoid circular import
    app.dashboardIsRunning = False # Disable the dashboard

    if lang not in tls.keys(): lang = "fr" # Handle invalid language
    dash.page_registry['lang'] = lang      # Provide the language to the callbacks

    return home.main_layout(lang) # Import the layout with the selected language


# Import callbacks
from tradingsimulator.Components import home as callbacks