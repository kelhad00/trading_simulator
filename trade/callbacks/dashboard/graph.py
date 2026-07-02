import time

from dash import Output, Input, State, callback, page_registry, ctx, no_update
from dash.exceptions import PreventUpdate
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
        value = options[0]['value'] if options else no_update

    return options, value


@callback(
    Output("periodic-updater", "interval"),
    Output("periodic-updater", "disabled", allow_duplicate=True),
    Output("pause-start-time", "data"),
    Output("total-paused-seconds", "data"),
    Input("update-time", "data"),
    Input("pause-button", "n_clicks"),
    State("periodic-updater", "disabled"),
    State("pause-start-time", "data"),
    State("total-paused-seconds", "data"),
    prevent_initial_call='initial_duplicate',
)
def update_interval(update_time, pause_clicks, currently_disabled, pause_start, total_paused):
    if ctx.triggered_id == "pause-button":
        if not pause_clicks:
            # n_clicks reset to 0 on page remount — ignore to avoid spurious pause
            raise PreventUpdate
        if not currently_disabled:
            # Pausing — record when the pause started
            return no_update, True, time.time(), no_update
        else:
            # Unpausing — accumulate the pause duration and clear the start time
            paused_for = time.time() - (pause_start or time.time())
            return no_update, False, None, (total_paused or 0) + paused_for
    return int(update_time), False, no_update, no_update


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
    Output('periodic-updater', 'disabled', allow_duplicate=True),
    Output('modal', 'opened', allow_duplicate=True),
    Output('session-start-time', 'data'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data'),
    State('session-start-time', 'data'),
    State('simulation-duration', 'data'),
    State('total-paused-seconds', 'data'),
    State('requests', 'data'),
    prevent_initial_call=True,
)
def update_graph(n, company, timestamp, session_start_time, simulation_duration, total_paused_seconds, requests):
    next_graph = ctx.triggered_id == 'periodic-updater'
    print(f"[GRAPH] tick triggered_id={ctx.triggered_id} next_graph={next_graph} company={company} ts={timestamp}")

    if next_graph:
        if session_start_time is None:
            # First tick of a new session — start the clock, skip end-condition check
            session_start_time = time.time()
        else:
            duration_secs = (simulation_duration or dlt.simulation_duration) * 60
            elapsed = time.time() - session_start_time - (total_paused_seconds or 0)
            data_done = (timestamp == get_last_timestamp(get_market_dataframe()))
            print(f"[GRAPH] elapsed={elapsed:.1f}s duration={duration_secs}s data_done={data_done}")

            if elapsed >= duration_secs or data_done:
                print("[GRAPH] simulation ended")
                return no_update, no_update, True, True, session_start_time

    try:
        # get_market_dataframe() is cached — only reads disk when file changes
        dftmp = get_market_dataframe()[company]

        fig, new_ts = create_graph(dftmp, timestamp, next_graph, 100)

        fig.update_layout(
            xaxis_title=tls[page_registry.get('lang', 'fr')]["market-graph"]['x'],
            yaxis_title=tls[page_registry.get('lang', 'fr')]["market-graph"]['y'],
            yaxis_tickprefix='€',
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(x=0, y=1.0),
            xaxis_rangeslider_visible=False,
            # uirevision keyed to company: preserves zoom/pan on periodic updates,
            # resets only when the user switches company
            uirevision=company,
            dragmode='pan',
        )

        fig.for_each_trace(
            lambda t: t.update(name=tls[page_registry.get("lang", "fr")]["market-graph"]['legend'][t.name])
        )

        for req in (requests or []):
            if req.get('company') != company:
                continue
            color = "green" if req['action'] == 'buy' else "red"
            label = f"{'Buy' if req['action'] == 'buy' else 'Sell'} {req['shares']}x @ €{req['price']}"
            fig.add_hline(
                y=req['price'],
                line_dash="dash",
                line_color=color,
                line_width=1,
                annotation_text=label,
                annotation_position="right",
                annotation_font_color=color,
                annotation_font_size=11,
            )

        # Data exhaustion: create_graph couldn't advance (idx past end of dataframe).
        # Render the last frame and end immediately — no frozen-tick gap before the modal.
        if next_graph and new_ts == timestamp:
            print("[GRAPH] data exhausted at", new_ts)
            return new_ts, fig, True, True, session_start_time

        print(f"[GRAPH] ok new_ts={new_ts}")
        return new_ts, fig, no_update, no_update, session_start_time

    except Exception as e:
        print("Error in update_graph:", e)
        return no_update, no_update, no_update, no_update, no_update


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
                name=tls[page_registry.get("lang", "fr")]["revenue-graph"]['totalRevenue'],
                x=df['asOfDate'], y=df['TotalRevenue']
            ),
            go.Bar(
                name=tls[page_registry.get("lang", "fr")]["revenue-graph"]['netIncome'],
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
    lang = page_registry.get('lang', 'fr')
    if value == tls[lang]['tab-market']:
        return {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'none'}


@callback(
    Output('nav-away-time', 'data'),
    Output('total-paused-seconds', 'data', allow_duplicate=True),
    Output('pause-start-time', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    State('session-start-time', 'data'),
    State('nav-away-time', 'data'),
    State('total-paused-seconds', 'data'),
    State('pause-start-time', 'data'),
    prevent_initial_call=True,
)
def handle_navigation_timer(pathname, session_start_time, nav_away, total_paused, pause_start):
    if session_start_time is None:
        raise PreventUpdate
    now = time.time()
    on_dashboard = pathname and pathname.startswith('/dashboard')
    if not on_dashboard and nav_away is None:
        # Leaving — flush any active pause segment into total, clear pause clock
        accumulated = (now - pause_start) if pause_start is not None else 0
        return now, (total_paused or 0) + accumulated, None
    elif on_dashboard and nav_away is not None:
        # Returning — accumulate away time
        paused_for = now - nav_away
        return None, (total_paused or 0) + paused_for, None
    raise PreventUpdate
