from dash import Output, Input, State
import dash


@dash.callback(
    Output('home-start-button', 'style'),
    Output('home-start-button-info', 'style'),
    Input('home-clock', 'n_intervals'),
)
def manage_home_start_button(n):
    from tradingsimulator.app import app

    if app.home_start_button_disabled:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'inline'}, {'display': 'none'}
