from dash import Dash, html, dcc, Output, Input, State, Patch, no_update, page_registry as dash_registry
from dash.exceptions import PreventUpdate
import dash

import emotrade as etd
from emotrade.Locales import translations as tls

import flask
from flask import request

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
'''OR'''
# server = Flask(__name__)
# app = Dash(__name__, server=server)


# Callbacks
@dash.callback(
    Output('stop-msg', 'hidden'),
    Output('stop-msg','children'),
    Input('quit-btn','n_clicks'),
    prevent_initial_call=True,
)
def stop_app(stop_btn):
    """ Shutting down the app
    """
    if stop_btn == 0: raise PreventUpdate # Avoid callback to be triggered at the first load 
    stop_execution()
    
    return False, tls[dash_registry['lang']]["stop-msg"]

def stop_execution():
    global keepPlot
    #stream.stop_stream()
    keepPlot=False

    # stop the Flask server
    server.shutdown() 
    print('Server shutting down ...')
    # AttributeError: 'Flask' object has no attribute 'shutdown'
    
    server_thread.join()
    print("Dash app stopped gracefully.")



