from dash import Dash, html, dcc
import dash

from tradesim.Layouts.dashboard import add_state_components
from tradesim.defaults import defaults

# Initialize Dash app
app = Dash(__name__,
    use_pages=True, # use_pages is used for multi-language support
    suppress_callback_exceptions=True, # Disable ids check because we use dynamic layout
)

# Provide the ability to set the layout after changing default values
def set_layout(self):
    """Set the layout of the app"""

    # This will be replaced by the page content (layout with the selected language)
    self.layout = html.Div([
        *add_state_components(),
        dash.page_container
    ])
app.set_layout = set_layout.__get__(app)

# Add default values to the app object
# It is highly recommended to change them only before the server is started
app.defaults = defaults
app.d = defaults # Alias

# It isn’t recommended to change default values after the server has been started
# So we provide another way from the app object to change secure values
# Manage the home page start button with the app object at runtime
app.home_start_button_disabled = app.d.home_start_button_disabled


if __name__ == '__main__':
	# Run app
    app.set_layout() # Set the layout of the app
    app.run_server(debug=True) #TODO: change to False when deploying