from dash import Dash, html, dcc
import dash

from emotrade.Layouts import dashboard

# Initialize Dash app
app = Dash(__name__,
    use_pages=True, # use_pages is used for multi-language support
)

# Set app layout
# This will be replaced by the page content (layout with the selected language)
app.layout = html.Div([
    *dashboard.global_variables,

    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']}", href=page["relative_path"], 
                    style = {'text-decoration': 'none', 'color': 'black', 'font-weight': 'bold', 'font-size': 20}
                ),style = {'display' : 'inline', 'margin' : 10}
            )
            for page in dash.page_registry.values()
        ], style = {'font-family': 'Arial'}
    ),

    dash.page_container
])

if __name__ == '__main__':
	# Run app
    app.run_server(debug=True) #TODO: change to False when deploying