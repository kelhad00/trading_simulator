from dash import Dash, html, dcc
import dash
import dash_mantine_components as dmc

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from trade.defaults import defaults as dlt
from trade.utils.market import get_first_timestamp, get_market_dataframe
from trade.utils.news import get_news_dataframe
from trade.utils.download import download_market_data

external_scripts = [
    {'src': 'https://cdn.tailwindcss.com'}
]

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_scripts=external_scripts
)

theme = {
    "defaultRadius": "md",
    "components": {
        "Paper": {
            "defaultProps": {
                "p": "xs",
                "withBorder": True,
            }
        }
    },
}

market_df = get_market_dataframe()
news_df = get_news_dataframe()

app.layout = dmc.MantineProvider([
    dmc.NotificationsProvider([
        html.Div(id="notifications"),
        html.Div(id="export"),

        dcc.Store(id='timestamp', data=get_first_timestamp(market_df, news_df, 100), storage_type="session"),
        dcc.Store(id='requests', data=[], storage_type="session"),
        dcc.Store(id='portfolio-shares', data={c: 0 for c in dlt.companies.keys()}, storage_type="session"),
        dcc.Store(id='portfolio-totals', data={c: 0 for c in dlt.companies.keys()}, storage_type="session"),
        dcc.Store(id='cashflow', data=dlt.initial_money, storage_type="session"),

        dcc.Store(id="market", storage_type="session"),
        dcc.Store(id="companies", data={**dlt.companies, **dlt.indexes}, storage_type="session"),

        dash.page_container
    ])
], theme=theme)

if __name__ == '__main__':
    path = dlt.data_path

    if not os.path.exists(path):
        print('Creating directory ' + path + ' at root of the project')
        os.mkdir(path)

    if not os.path.exists(os.path.join(path, "market_data.csv")) \
            or not os.path.exists(os.path.join(path, "revenue.csv")):
        print('\nDownloading market data...\n')
        download_market_data()

    if not os.path.exists(os.path.join(path, "news.csv")):
        print('\nYou need to add the `news.csv` file into the ' + path + ' folder\n')
        quit()

    app.run_server(debug=True)