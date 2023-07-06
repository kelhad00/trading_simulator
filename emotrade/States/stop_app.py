from dash import html, dcc, Output, Input, State, Patch, no_update, page_registry as dash_registry
from dash.exceptions import PreventUpdate
import dash

import emotrade as etd
from emotrade.Locales import translations as tls

# Callbacks
@dash.callback(
    Output('stop-msg', 'hidden'),
    Output('stop-msg','children'),
    Input('quit-btn','n_clicks'),
    prevent_initial_call=True,
)
def stop_app(stop_btn):
    """ Information Message printing
    """
    if stop_btn == 0: raise PreventUpdate # Avoid callback to be triggered at the first load 
    
    return False, tls[dash_registry['lang']]["stop-msg"]