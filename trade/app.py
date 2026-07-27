from dash import Dash, html, dcc, clientside_callback, Input, Output, State
import dash
import dash_mantine_components as dmc

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

APP_MODE = os.getenv('APP_MODE', 'config')

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
    "colorScheme": "light",
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

def _ensure_data_dirs():
    path = dlt.data_path
    for subdir in ("", "export", "exports"):
        d = os.path.join(path, subdir) if subdir else path
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

_ensure_data_dirs()

market_df = get_market_dataframe()

portfolio_value = {ticker: 0 for ticker in dlt.companies_list.keys()}

app.layout = dmc.MantineProvider([
    dmc.NotificationsProvider([
        dcc.Store(id="color-scheme-store", data="light", storage_type="local"),
        html.Div(id="notifications"),

        # Global location tracker — lets navigation-triggered callbacks re-fire
        dcc.Location(id="url", refresh=False),

        dcc.Store(id='timestamp', data=get_first_timestamp(market_df, 100), storage_type="session"),
        dcc.Store(id='requests', data=[], storage_type="session"),
        dcc.Store(id='portfolio-shares', data=portfolio_value, storage_type="session"),
        dcc.Store(id='portfolio-totals', data=portfolio_value, storage_type="session"),
        dcc.Store(id='cost-basis', data={}, storage_type="session"),
        dcc.Store(id='sold-data', data={}, storage_type="session"),
        dcc.Store(id='cashflow', data=dlt.initial_money, storage_type="session"),

        dcc.Store(id="companies", data=dlt.companies_list, storage_type="local"),
        dcc.Store(id="nb_export", data=len(os.listdir(os.path.join(dlt.data_path, "exports"))), storage_type="session"),

        # Advanced settings
        dcc.Store(id="initial-cashflow", data=dlt.initial_money, storage_type="session"),
        dcc.Store(id="max-requests", data=dlt.max_requests, storage_type="session"),
        dcc.Store(id="update-time", data=dlt.update_time, storage_type="session"),
        dcc.Store(id="simulation-duration", data=dlt.simulation_duration, storage_type="local"),

        # Session timer — records time.time() on first periodic-updater tick
        dcc.Store(id="session-start-time", data=None, storage_type="session"),

        # News notification tracking — last timestamp that was notified
        dcc.Store(id="last-notified-ts", data=None, storage_type="session"),

        # Pause time tracking — freeze the simulation timer while paused
        dcc.Store(id="pause-start-time", data=None, storage_type="session"),
        dcc.Store(id="total-paused-seconds", data=0, storage_type="session"),
        dcc.Store(id="nav-away-time", data=None, storage_type="session"),

        # Trigger for hard browser redirect after session ends
        dcc.Store(id="do-redirect", data=False, storage_type="memory"),

        # Right-click context menu on chart
        dcc.Store(id="ctx-right-click", data=None, storage_type="memory"),
        dcc.Store(id="ctx-setup-done", data=False, storage_type="memory"),
        dcc.Store(id="ctx-left-click", data=None, storage_type="memory"),

        dcc.Store(id='imported-session-name', storage_type='memory'),
        html.Div(id="_sname-sink", style={"display": "none"}),
        dcc.Download(id="download-session"),

        dash.page_container
    ])
], theme=theme, id="mantine-provider")

clientside_callback(
    """function(n, scheme) {
        if (!n) return scheme || 'light';
        return scheme === 'dark' ? 'light' : 'dark';
    }""",
    Output("color-scheme-store", "data", allow_duplicate=True),
    Input("theme-toggle-home", "n_clicks"),
    State("color-scheme-store", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    """function(n, scheme) {
        if (!n) return scheme || 'light';
        return scheme === 'dark' ? 'light' : 'dark';
    }""",
    Output("color-scheme-store", "data", allow_duplicate=True),
    Input("theme-toggle-dashboard", "n_clicks"),
    State("color-scheme-store", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    """function(scheme) {
        var s = scheme || 'light';
        var bg = s === 'dark' ? '#1a1b1e' : '#f3f4f6';
        document.body.style.backgroundColor = bg;
        document.documentElement.style.backgroundColor = bg;
        return {
            colorScheme: s,
            defaultRadius: 'md',
            components: {
                Paper: { defaultProps: { p: 'xs', withBorder: true } }
            }
        };
    }""",
    Output("mantine-provider", "theme"),
    Input("color-scheme-store", "data"),
)

clientside_callback(
    """function(scheme, fig) {
        if (!fig || !fig.layout) return window.dash_clientside.no_update;
        var dark = scheme === 'dark';
        var bg = dark ? '#1a1b1e' : 'white';
        var fc = dark ? '#c1c2c5' : '#333333';
        var gc = dark ? '#373A40' : '#eeeeee';
        return Object.assign({}, fig, {
            layout: Object.assign({}, fig.layout, {
                paper_bgcolor: bg,
                plot_bgcolor: bg,
                font: Object.assign({}, fig.layout.font || {}, { color: fc }),
                xaxis: Object.assign({}, fig.layout.xaxis || {}, { gridcolor: gc }),
                yaxis: Object.assign({}, fig.layout.yaxis || {}, { gridcolor: gc }),
            })
        });
    }""",
    Output("company-graph", "figure", allow_duplicate=True),
    Input("color-scheme-store", "data"),
    State("company-graph", "figure"),
    prevent_initial_call=True,
)

clientside_callback(
    """function(scheme, fig) {
        if (!fig || !fig.layout) return window.dash_clientside.no_update;
        var dark = scheme === 'dark';
        var bg = dark ? '#1a1b1e' : 'white';
        var fc = dark ? '#c1c2c5' : '#333333';
        var gc = dark ? '#373A40' : '#eeeeee';
        return Object.assign({}, fig, {
            layout: Object.assign({}, fig.layout, {
                paper_bgcolor: bg,
                plot_bgcolor: bg,
                font: Object.assign({}, fig.layout.font || {}, { color: fc }),
                xaxis: Object.assign({}, fig.layout.xaxis || {}, { gridcolor: gc }),
                yaxis: Object.assign({}, fig.layout.yaxis || {}, { gridcolor: gc }),
            })
        });
    }""",
    Output("revenue-graph", "figure", allow_duplicate=True),
    Input("color-scheme-store", "data"),
    State("revenue-graph", "figure"),
    prevent_initial_call=True,
)


def run():
    path = dlt.data_path

    if APP_MODE == 'config':
        if not os.path.exists(os.path.join(path, "generated_data.csv")) \
                or not os.path.exists(os.path.join(path, "revenue.csv")):
            print('\nDownloading market data...\n')
            download_market_data()

    port = int(os.getenv('APP_PORT', 8050))
    app.run_server(debug=False, threaded=True, port=port)