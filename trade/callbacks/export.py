
import time

import pandas as pd

import dash_mantine_components as dmc
from dash import Output, Input, State, html, callback, no_update, page_registry as dash_registry, Patch, ALL, ctx
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.Locales import translations as tls
from trade.utils.create_table import create_table, create_selectable_table
from trade.utils.market import get_price_dataframe
from trade.utils.store.export import export_data



@callback(
    Output("export", "children"),

    Input("company-selector", "value"),
    Input('description-title', 'children'),
    Input('segmented', "value"),
    Input("action-input", "value"),

    State('cashflow', 'data'),
    State('timestamp', 'data'),
    State('portfolio-shares', 'data'),
    State("portfolio-totals", "data"),
    State("requests", "data"),
)
def export_display_update(company, title, graph_segmented, request_segmented, cashflow, timestamp, shares, totals, requests):
    print("title", title)
    export_data(timestamp, requests, cashflow, shares, totals, company, title, graph_segmented, request_segmented)
    return no_update
