from dash import Output, Input, State, callback, page_registry, ctx, no_update
import plotly.graph_objects as go
import pandas as pd

from trade.utils.graph.candlestick_charts import create_graph
from trade.utils.market import get_market_dataframe, get_last_timestamp, get_revenues_dataframe
from trade.locales import translations as tls
from trade.defaults import defaults as dlt


@callback(
    Output("company-selector", "data"),
    Output("company-selector", "value"),
    Input("companies", "data"),
    State("company-selector", "data"),
)
def update_select_companies_options(companies, select_options):
    options = [{"label": value["label"], "value": key} for key, value in companies.items() if value["got_charts"]]

    if select_options == options:
        value = no_update
    else:
        value = list(companies.keys())[0]

    return options, value


@callback(
    Output("modal", "opened", allow_duplicate=True),
    Input("timestamp", "data"),
    prevent_initial_call=True
)
def update_modal(timestamp):
    # get_market_dataframe() is now cached — negligible cost
    if timestamp == get_last_timestamp(get_market_dataframe()):
        return True
    return False


@callback(
    Output("periodic-updater", "interval"),
    Output("periodic-updater", "disabled"),
    Input("update-time", "data"),
    Input("pause-button", "n_clicks"),
    State("periodic-updater", "disabled"),
)
def update_interval(update_time, pause_clicks, currently_disabled):
    if ctx.triggered_id == "pause-button":
        return no_update, not currently_disabled
    return int(update_time), False


@callback(
    Output("timer", "children"),
    Input("timestamp", "data"),
)
def cb_update_timestamp(timestamp):
    timestamp = pd.to_datetime(timestamp)
    return timestamp.strftime("%Y-%m-%d")


@callback(
    Output('timestamp', 'data'),
    Output('company-graph', 'figure'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data')
)
def update_graph(n, company, timestamp, range=100):
    try:
        next_graph = ctx.triggered_id == 'periodic-updater'

        # get_market_dataframe() is cached — only reads disk when file changes
        dftmp = get_market_dataframe()[company]

        fig, timestamp = create_graph(dftmp, timestamp, next_graph, range)

        fig.update_layout(
            xaxis_title=tls[page_registry['lang']]["market-graph"]['x'],
            yaxis_title=tls[page_registry['lang']]["market-graph"]['y'],
            yaxis_tickprefix='€',
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(x=0, y=1.0),
            xaxis_rangeslider_visible=False,
            # uirevision keyed to company: preserves zoom/pan on periodic updates,
            # resets only when the user switches company
            uirevision=company,
        )

        fig.for_each_trace(
            lambda t: t.update(name=tls[page_registry["lang"]]["market-graph"]['legend'][t.name])
        )

        return timestamp, fig

    except Exception as e:
        print("Error", e)
        return no_update, no_update


@callback(
    Output('revenue-graph', 'figure'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data'),
    State("companies", "data")
)
def update_revenue(n, company, timestamp, companies):
    try:
        if companies[company]['activity'] == "Indice":
            return no_update

        ts = pd.to_datetime(timestamp)

        # Revenue data is annual — only rebuild on periodic tick when a new year
        # has just started in the simulation (first 7 days of January).
        # The graph is always fully rebuilt when the user switches company.
        if ctx.triggered_id == 'periodic-updater':
            if not (ts.month == 1 and ts.day <= 7):
                return no_update

        # get_revenues_dataframe() is cached — only reads disk when file changes
        df = get_revenues_dataframe()

        df = df[company].T.reset_index()
        df['asOfDate'] = pd.to_datetime(df['asOfDate']).dt.year
        df['NetIncome'] = pd.to_numeric(df['NetIncome'], errors='coerce')
        df['TotalRevenue'] = pd.to_numeric(df['TotalRevenue'], errors='coerce')

        year = ts.year
        df = df.loc[df['asOfDate'] < year]

        fig = go.Figure(data=[
            go.Bar(
                name=tls[page_registry["lang"]]["revenue-graph"]['totalRevenue'],
                x=df['asOfDate'], y=df['TotalRevenue']
            ),
            go.Bar(
                name=tls[page_registry["lang"]]["revenue-graph"]['netIncome'],
                x=df['asOfDate'], y=df['NetIncome']
            )
        ])
        fig.update_layout(
            yaxis_tickprefix='€',
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(x=0, y=1.0),
            uirevision=company,
        )

        return fig

    except Exception as e:
        print("Error", e)
        return no_update


@callback(
    Output('revenue-graph', 'style'),
    Output('company-graph', 'style'),
    Input('segmented', "value")
)
def toggle_graph_type(value):
    lang = page_registry['lang']
    if value == tls[lang]['tab-market']:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'none'}
