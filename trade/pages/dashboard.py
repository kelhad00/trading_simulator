import os

import dash
from dash import Input, Output, callback

from trade.layouts.dashboard.layout import main_layout

# Don't delete this import
from trade.callbacks.dashboard import news, portfolio, graph, request, export, reminders

dash.register_page(__name__, path="/dashboard")

if os.getenv('APP_MODE') == 'config':
    @callback(
        Output('url', 'pathname', allow_duplicate=True),
        Input('url', 'pathname'),
        prevent_initial_call=True,
    )
    def _guard_dashboard(pathname):
        if pathname and pathname.startswith('/dashboard'):
            return '/'
        return pathname


def layout(lang="fr", **kwargs):
    dash.page_registry['lang'] = lang
    return main_layout(lang)




