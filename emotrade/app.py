from dash import Dash, page_container as dash_page_container

from emotrade.Locales import translations as tls


# Initialize Dash app
app = Dash(__name__,
    use_pages=True, # use_pages is used for multi-language support
)

# Set app layout
# This will be replaced by the page content (layout with the selected language)
app.layout = dash_page_container

# Import callbacks
# This is done after app initialization to avoid circular imports.
from emotrade.States import import_data, save_state
from emotrade.Components import graph, portfolio, requests, news


if __name__ == '__main__':
	# Run app
    app.run_server(debug=True) #TODO: change to False when deploying