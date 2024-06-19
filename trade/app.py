from dash import Dash, html, dcc
import dash
import dash_mantine_components as dmc

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from trade.defaults import defaults as dlt
from trade.utils.market import get_first_timestamp, get_market_dataframe
from trade.utils.news import get_news_dataframe

external_scripts = [
    {'src': 'https://cdn.tailwindcss.com'}
]

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_scripts=external_scripts
)

market_df = get_market_dataframe()
news_df = get_news_dataframe()

app.layout = dmc.MantineProvider([
    dcc.Store(id='timestamp', data=get_first_timestamp(market_df, news_df, 100), storage_type="session"),
    dcc.Store(id='requests', data=[], storage_type="session"),
    dcc.Store(id='portfolio-shares', data={c: 0 for c in dlt.companies.keys()}, storage_type="session"),
    dcc.Store(id='portfolio-totals', data={c: 0 for c in dlt.companies.keys()}, storage_type="session"),
    dcc.Store(id='cashflow', data=dlt.initial_money, storage_type="session"),

    dcc.Store(id="market", storage_type="session"),
    dcc.Store(id="companies", data={**dlt.companies, **dlt.indexes}, storage_type="session"),

    dash.page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)