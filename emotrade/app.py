from dash import Dash

from emotrade.Layouts import layout

# Initialize Dash app
app = Dash(__name__)

# Import the layout
app.layout = layout.main_layout

# Import callbacks
# This is done after app initialization to avoid circular imports.
from emotrade.States import import_data, save_state
from emotrade.Components import graph, portfolio, requests, news


if __name__ == '__main__':
	# Run app
    app.run_server(debug=True) #TODO: change to False when deploying