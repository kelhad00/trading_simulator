from dash import Dash, html, dcc, clientside_callback, Input, Output, State
import dash
import dash_mantine_components as dmc

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

APP_MODE = os.getenv('APP_MODE', 'config')

from trade.defaults import defaults as dlt
from trade.utils.logs import setup_logging, get_logger

# Terminal messages: LOG_LEVEL in .env (DEBUG / INFO / WARNING), see utils/logs.py
setup_logging()
logger = get_logger("app")
from trade.utils.market import get_start_timestamp, get_market_dataframe
from trade.utils.news import get_news_dataframe
from trade.utils.download import download_market_data

# No scripts from the internet: the app must work offline in the lab. The page
# styling (Tailwind) and the icons are files in trade/assets/ (tailwind.css,
# icons.js), loaded automatically by Dash. To rebuild them: README, "Working offline".
external_scripts = []

_anti_flash_script = """
<script>
(function(){
  try {
    var s = JSON.parse(localStorage.getItem('color-scheme-store'));
    if (s === 'dark') {
      document.documentElement.style.backgroundColor = '#1a1b1e';
      document.body.style.backgroundColor = '#1a1b1e';
    }
    var ce = JSON.parse(localStorage.getItem('color-enabled'));
    if (ce === true) {
      document.body.style.filter = 'invert(100%) hue-rotate(180deg)';
    }
  } catch(e) {}
})();
</script>
"""

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks="initial_duplicate",
    external_scripts=external_scripts,
    index_string="""<!DOCTYPE html>
<html>
  <head>
    {%metas%}
    <title>{%title%}</title>
    """ + _anti_flash_script + """
    {%favicon%}
    {%css%}
  </head>
  <body>
    {%app_entry%}
    <footer>
      {%config%}
      {%scripts%}
      {%renderer%}
    </footer>
  </body>
</html>"""
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

        # Automatic news (after confirming charts) runs in a background thread: the
        # job id is kept here and the page checks it every 2 s until it finishes,
        # then shows a success or error pop-up (callbacks/settings/charts/modal.py).
        dcc.Store(id="auto-news-job", data=None, storage_type="memory"),
        dcc.Interval(id="auto-news-poll", interval=2000, disabled=True),

        # Global location tracker — lets navigation-triggered callbacks re-fire
        dcc.Location(id="url", refresh=False),

        dcc.Store(id='timestamp', data=get_start_timestamp(market_df), storage_type="session"),
        # Moving candles: step reached by the candle at `timestamp` (1..steps-per-candle).
        # None = the candle is closed, e.g. at session start or after a reset.
        dcc.Store(id='candle-step', data=None, storage_type="session"),
        # This tab's session: its logs go to data/exports/<session-id>/ (utils/export.py).
        # Set when the dashboard opens; a new one after Reset or a session import.
        dcc.Store(id='session-id', data=None, storage_type="session"),
        dcc.Store(id='requests', data=[], storage_type="session"),
        # Whether the market graph should auto-scroll to the live edge on each
        # update. Set to False when the user manually pans/zooms away, and
        # back to True when they switch company or click "Reset axes".
        dcc.Store(id='graph-auto-follow', data=True, storage_type="memory"),
        # The x-axis window the user manually panned/zoomed to, re-applied on
        # every update while graph-auto-follow is False so the view stays put.
        dcc.Store(id='graph-manual-range', data=None, storage_type="memory"),
        dcc.Store(id='portfolio-shares', data=portfolio_value, storage_type="session"),
        dcc.Store(id='portfolio-totals', data=portfolio_value, storage_type="session"),
        dcc.Store(id='cost-basis', data={}, storage_type="session"),
        dcc.Store(id='sold-data', data={}, storage_type="session"),
        # Cash belongs to one participant's game, like shares and orders: kept per
        # tab ("session"), so a new tab never inherits the previous participant's
        # cash. Its starting value comes from "initial-cashflow" (kept in the
        # browser, set by an imported session): see start_cash_for_new_tab in
        # callbacks/reset.py.
        dcc.Store(id='cashflow', data=dlt.initial_money, storage_type="session"),

        dcc.Store(id="companies", data=dlt.companies_list, storage_type="local"),
        dcc.Store(id="nb_export", data=len(os.listdir(os.path.join(dlt.data_path, "exports"))), storage_type="session"),

        # Advanced settings — imported together with companies/simulation-duration as
        # part of the same session.zip, so they need the same "local" persistence to
        # survive a closed/reopened browser tab (sessionStorage does not).
        dcc.Store(id="initial-cashflow", data=dlt.initial_money, storage_type="local"),
        dcc.Store(id="max-requests", data=dlt.max_requests, storage_type="local"),
        dcc.Store(id="update-time", data=dlt.update_time, storage_type="local"),
        dcc.Store(id="steps-per-candle", data=dlt.steps_per_candle, storage_type="local"),
        # Candles of history already shown when a session starts (Settings -> Advanced)
        dcc.Store(id="initial-bars", data=dlt.initial_reveal_bars, storage_type="local"),
        dcc.Store(id="simulation-duration", data=dlt.simulation_duration, storage_type="local"),
        dcc.Store(id="news-font-size", data=dlt.news_font_size, storage_type="local"),

        # Session timer — records time.time() on first periodic-updater tick
        dcc.Store(id="session-start-time", data=None, storage_type="session"),

        # News notification tracking — last timestamp that was notified
        dcc.Store(id="last-notified-ts", data=None, storage_type="session"),

        # Notification settings — filter by sentiment and optional early-warning offset
        dcc.Store(id="notif-enabled", data=True, storage_type="local"),
        # Time reminders during a session ("5 minutes remaining"...), Settings -> News
        dcc.Store(id="reminders-enabled", data=True, storage_type="local"),
        dcc.Store(id="color-enabled", data=False, storage_type="local"),
        dcc.Store(id="notif-filter", data=["positive", "negative", "neutral"], storage_type="local"),
        dcc.Store(id="notif-offset", data=0, storage_type="local"),

        # Pause time tracking — freeze the simulation timer while paused
        dcc.Store(id="pause-start-time", data=None, storage_type="session"),
        dcc.Store(id="total-paused-seconds", data=0, storage_type="session"),
        dcc.Store(id="nav-away-time", data=None, storage_type="session"),

        # Time reminder tracking — keys of reminders already shown this session
        dcc.Store(id="shown-reminders", data=[], storage_type="session"),

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

# The Dark / Light menu option was removed: dark is now only the "dark mode for
# the simulation" toggle (color-enabled). Keep the theme on light so an old saved
# value, or an old session file, can't leave the page dark with no way back, or
# combine with the toggle's inversion and turn the page light again.
clientside_callback(
    """function(scheme) {
        return scheme === 'light' ? window.dash_clientside.no_update : 'light';
    }""",
    Output("color-scheme-store", "data", allow_duplicate=True),
    Input("color-scheme-store", "data"),
    prevent_initial_call='initial_duplicate',
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

_graph_patch_js = """function(scheme, fig) {
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
}"""

clientside_callback(
    _graph_patch_js,
    Output("chart", "figure", allow_duplicate=True),
    Input("color-scheme-store", "data"),
    State("chart", "figure"),
    prevent_initial_call=True,
)

clientside_callback(
    _graph_patch_js,
    Output("news-chart", "figure", allow_duplicate=True),
    Input("color-scheme-store", "data"),
    State("news-chart", "figure"),
    prevent_initial_call=True,
)

clientside_callback(
    """function(enabled) {
        document.body.style.filter = (enabled === true) ? 'invert(100%) hue-rotate(180deg)' : '';
        return window.dash_clientside.no_update;
    }""",
    Output("color-enabled", "data", allow_duplicate=True),
    Input("color-enabled", "data"),
    prevent_initial_call='initial_duplicate',
)


def run():
    path = dlt.data_path

    if APP_MODE == 'config':
        if not os.path.exists(os.path.join(path, "generated_data.csv")) \
                or not os.path.exists(os.path.join(path, "revenue.csv")):
            logger.info("Downloading market data...")
            download_market_data()

    port = int(os.getenv('APP_PORT', 8050))
    app.run_server(debug=False, threaded=True, port=port)