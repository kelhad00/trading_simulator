import os

import dash
from dash import Input, Output, callback

from trade.layouts.settings.layout import main_layout

# Don't delete these imports — they register callbacks as side-effects
from trade.callbacks.settings import stocks, advanced, news, upload, revenues
from trade.callbacks.settings.charts import charts, modal
from trade.callbacks.settings import session_export  # noqa: F401

dash.register_page(__name__, path="/settings")

if os.getenv('APP_MODE') == 'runtime':
    @callback(
        Output('url', 'pathname', allow_duplicate=True),
        Input('url', 'pathname'),
        prevent_initial_call=True,
    )
    def _guard_settings(pathname):
        if pathname and pathname.startswith('/settings'):
            return '/'
        return pathname


def layout(lang="fr", **kwargs):
    dash.page_registry['lang'] = lang
    return main_layout(lang)