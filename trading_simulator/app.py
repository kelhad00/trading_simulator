from dash import Dash

from trading_simulator.Layouts import layout

# Initialize Dash app
app = Dash(__name__)

# Import the layout
app.layout = layout.main_layout

# Import callbacks
# This is done after app initialization to avoid circular imports.
from trading_simulator.States import import_state, import_data, save_state
from trading_simulator.Components import graph, portfolio, requests, news


if __name__ == '__main__':
	# Run app
    app.run_server(debug=True) #TODO: change to False when deploying