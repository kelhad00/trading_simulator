import dash

from emotrade.Layouts import home
from emotrade.Locales import translations as tls

dash.register_page(
    __name__,
    path_template="/<lang>/"
)


def layout(lang="fr"):
    if lang not in tls.keys(): lang = "fr" # Handle invalid language
    dash.page_registry['lang'] = lang      # Provide the language to the callbacks

    return home.main_layout(lang) # Import the layout with the selected language 


#Import callbacks
from emotrade.States import stop_app