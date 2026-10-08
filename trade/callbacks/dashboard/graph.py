import time

from dash import Output, Input, State, callback, page_registry, ctx, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import pandas as pd
from dash_iconify import DashIconify

from trade.utils.graph.candlestick_charts import create_graph
from trade.utils.candle_steps import (
    normalize as normalize_step, is_forming, partial_candle, market_time, step_minutes,
)
from trade.utils.export import log_session_event, write_log_info
from trade.utils.market import get_market_dataframe, get_last_timestamp, get_revenues_dataframe
from trade.utils.news import get_news_dataframe
from trade.utils.news_timing import appeared_count, now_position
from trade.callbacks.dashboard.reminders import due_reminders
from trade.locales import translations as tls
from trade.defaults import defaults as dlt
from trade.utils.logs import get_logger

logger = get_logger("graph")


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
    Input("update-time", "data"),
)
def sync_interval(update_time):
    return int(update_time)


@callback(
    Output("periodic-updater", "disabled", allow_duplicate=True),
    Output("pause-start-time", "data"),
    Output("total-paused-seconds", "data"),
    Output("pause-button", "children"),
    Output("pause-button", "icon"),
    Input("pause-button", "n_clicks"),
    State("periodic-updater", "disabled"),
    State("pause-start-time", "data"),
    State("total-paused-seconds", "data"),
    State("timestamp", "data"),
    State("cashflow", "data"),
    State("company-selector", "value"),
    State("candle-step", "data"),
    State("steps-per-candle", "data"),
    State("session-id", "data"),
    prevent_initial_call=True,
)
def toggle_pause(pause_clicks, currently_disabled, pause_start, total_paused, timestamp, cashflow, company, candle_step, steps_per_candle,
                 session_id=None):
    if not pause_clicks:
        # n_clicks reset to 0 on page remount — ignore to avoid spurious pause
        raise PreventUpdate
    when = market_time(timestamp, candle_step, steps_per_candle)
    if not currently_disabled:
        # Pausing — record when the pause started
        log_session_event("session-pause", when, cashflow, company, session_id)
        return True, time.time(), no_update, "Resume", DashIconify(icon="carbon:play")
    else:
        # Unpausing — accumulate the pause duration and clear the start time
        paused_for = time.time() - (pause_start or time.time())
        log_session_event("session-resume", when, cashflow, company, session_id)
        return False, None, (total_paused or 0) + paused_for, "Pause", DashIconify(icon="carbon:pause")


def timer_label(timestamp, candle_step, steps_per_candle):
    """Date shown above the chart (sent by update_graph, together with the chart)."""
    date = pd.to_datetime(timestamp).strftime("%Y-%m-%d")
    step, n_steps = normalize_step(candle_step, steps_per_candle)
    if n_steps == 1:
        return date
    # Moving candles: show the market clock inside the candle (15 / 30 / 45 / 60 min)
    return f"{date} · {step_minutes(step, n_steps)} min"


@callback(
    Output('graph-auto-follow', 'data'),
    Output('graph-manual-range', 'data'),
    Input('company-graph', 'relayoutData'),
    Input('company-selector', 'value'),
    prevent_initial_call=True,
)
def track_graph_auto_follow(relayout_data, company):
    # Switching company always resumes auto-follow for the new chart.
    if ctx.triggered_id == 'company-selector':
        return True, None

    if not relayout_data:
        raise PreventUpdate

    # "Reset axes" (modebar button or double-click) re-enables auto-follow.
    if relayout_data.get('xaxis.autorange') or relayout_data.get('autosize'):
        return True, None

    # A manual pan or zoom disables auto-follow until the user resets it.
    # Remember exactly where they left the view so every subsequent update
    # can be pinned back to that same window instead of re-autoranging.
    if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
        manual_range = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
        return False, manual_range

    raise PreventUpdate


@callback(
    Output('timestamp', 'data'),
    Output('company-graph', 'figure'),
    Output('periodic-updater', 'disabled', allow_duplicate=True),
    Output('modal', 'opened', allow_duplicate=True),
    Output('session-start-time', 'data'),
    Output('candle-step', 'data'),
    # Sent together with the chart instead of as separate updates: every separate
    # update makes the browser redraw the whole screen, which slows it down.
    Output('timer', 'children'),
    Output('news-clock', 'data'),
    Output('revenue-year', 'data'),
    Output('notifications', 'children', allow_duplicate=True),
    Output('shown-reminders', 'data'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data'),
    State('session-start-time', 'data'),
    State('simulation-duration', 'data'),
    State('total-paused-seconds', 'data'),
    Input('requests', 'data'),
    Input('color-scheme-store', 'data'),
    State('graph-auto-follow', 'data'),
    State('graph-manual-range', 'data'),
    State('cashflow', 'data'),
    State('candle-step', 'data'),
    State('steps-per-candle', 'data'),
    State('initial-bars', 'data'),
    # Only used to record the session's settings in log-info.json
    State('update-time', 'data'),
    State('max-requests', 'data'),
    State('initial-cashflow', 'data'),
    State('companies', 'data'),
    State('session-id', 'data'),
    # Last values sent with the chart: only sent again when they change
    State('news-clock', 'data'),
    State('revenue-year', 'data'),
    State('notif-offset', 'data'),
    State('shown-reminders', 'data'),
    State('reminders-enabled', 'data'),
    prevent_initial_call=True,
)
def update_graph(n, company, timestamp, session_start_time, simulation_duration, total_paused_seconds, requests, color_scheme, auto_follow, manual_range, cashflow, candle_step, steps_per_candle, initial_bars,
                 update_time=None, max_requests=None, initial_cashflow=None, companies=None, session_id=None,
                 news_clock=None, revenue_year=None, notif_offset=0, shown_reminders=None, reminders_enabled=True):
    following = auto_follow if auto_follow is not None else True
    next_graph = ctx.triggered_id == 'periodic-updater'
    step, n_steps = normalize_step(candle_step, steps_per_candle)
    logger.debug("tick triggered_id=%s next_graph=%s company=%s ts=%s step=%s/%s",
                 ctx.triggered_id, next_graph, company, timestamp, step, n_steps)

    if next_graph:
        if session_start_time is None:
            # First tick of a new session — start the clock, skip end-condition check
            session_start_time = time.time()
            log_session_event("session-start", market_time(timestamp, step, n_steps), cashflow, company, session_id)
            logger.info("Session started (%s min)", simulation_duration or dlt.simulation_duration)
            try:
                # Automatic record of the code version and settings this session runs with
                write_log_info({
                    "simulation_duration_min": simulation_duration or dlt.simulation_duration,
                    "update_time_ms": int(update_time or dlt.update_time),
                    "steps_per_candle": n_steps,
                    "history_candles_at_start": int(initial_bars or dlt.initial_reveal_bars),
                    "max_requests": max_requests or dlt.max_requests,
                    "initial_cashflow": initial_cashflow or dlt.initial_money,
                    "first_market_timestamp": str(timestamp),
                    "companies": sorted(k for k, v in (companies or {}).items() if v.get("got_charts")),
                }, session_id)
            except Exception as e:  # recording must never stop a session
                logger.warning("Could not write log-info.json: %s", e)
        else:
            duration_secs = (simulation_duration or dlt.simulation_duration) * 60
            elapsed = time.time() - session_start_time - (total_paused_seconds or 0)
            # With moving candles the data is only done once the last candle has closed
            data_done = (timestamp == get_last_timestamp(get_market_dataframe())) and step >= n_steps
            logger.debug("elapsed=%.1fs duration=%ss data_done=%s", elapsed, duration_secs, data_done)

            if elapsed >= duration_secs or data_done:
                logger.info("Session ended (%s)", "end of data" if data_done else "time is up")
                log_session_event("session-finish", market_time(timestamp, step, n_steps), cashflow, company, session_id)
                return (no_update, no_update, True, True, session_start_time, no_update) + _NOTHING_ELSE

    # Moving candles: a tick moves the forming candle one step (15 -> 30 -> 45 min);
    # only once it has closed does the next candle start and the timestamp advance.
    # With 1 step per candle every tick advances, as before.
    advance = next_graph and step >= n_steps
    new_step = (1 if advance else step + 1) if next_graph else step

    def sent_with_chart(ts, shown_step):
        """Clock label, news clock, revenue year and time reminders for this moment."""
        clock = _news_clock(ts, shown_step, n_steps, notif_offset, session_id)
        year = pd.Timestamp(ts).year
        popups, shown = no_update, no_update
        if next_graph:
            try:
                popups, shown = due_reminders(session_start_time, simulation_duration, total_paused_seconds,
                                              shown_reminders, reminders_enabled)
            except PreventUpdate:
                pass
        return (timer_label(ts, shown_step, n_steps),
                clock if clock != news_clock else no_update,
                year if year != revenue_year else no_update,
                popups, shown)

    def forming_candle(ts):
        # ts == timestamp while advancing = no next candle (end of data): stays closed
        if not is_forming(new_step, n_steps) or (advance and ts == timestamp):
            return None
        return partial_candle(company, ts, new_step, n_steps)

    try:
        # get_market_dataframe() is cached — only reads disk when file changes
        dftmp = get_market_dataframe()[company]

        fig, new_ts = create_graph(dftmp, timestamp, advance, int(initial_bars or dlt.initial_reveal_bars), follow=following,
                                   # zoomed in: date labels adapt to the candles on screen
                                   view_range=manual_range if (not following and manual_range) else None,
                                   partial=forming_candle)

        if not following and manual_range:
            # Pin the view to exactly where the user left it — sending no
            # range at all lets Plotly re-autorange over the full (now much
            # bigger) history and squeeze every candle into view, which is
            # not what we want while the user is browsing the past.
            fig.update_xaxes(range=manual_range)

        fig.update_layout(
            # No axis titles: the date is shown above the chart and the axis
            # is already labelled with € prices, so this space goes to candles.
            xaxis_title=None,
            yaxis_title=None,
            # Toolbar in a horizontal strip in the top margin instead of a
            # vertical column covering the price axis.
            modebar=dict(orientation='h'),
            yaxis_tickprefix='€',
            yaxis_tickformat=',.2f',
            margin=dict(l=0, r=90, t=30, b=0),
            # Legend in one row just above the plot so it never covers candles.
            legend=dict(orientation='h', x=0, y=1.0, xanchor='left', yanchor='bottom'),
            xaxis_rangeslider_visible=False,
            # uirevision keyed to company: preserves zoom/pan on periodic updates,
            # resets only when the user switches company
            uirevision=company,
            dragmode='pan',
            template='plotly_dark' if color_scheme == 'dark' else 'plotly_white',
        )

        if following:
            # Fixed-slot playback: the server sets the x range (all slots) and
            # the padded y range on every frame, so give both axes a fresh
            # revision each tick. Otherwise uirevision would keep an old range
            # (or a "reset axes" autorange) and ignore the new one.
            fig.update_layout(
                xaxis_uirevision=f"{company}|{new_ts}",
                yaxis_uirevision=f"{company}|{new_ts}",
            )

        fig.for_each_trace(
            lambda t: t.update(name=tls[page_registry.get("lang", "fr")]["market-graph"]['legend'][t.name])
        )

        for req in (requests or []):
            if req.get('company') != company:
                continue
            color = "green" if req['action'] == 'buy' else "red"
            label = f"{'Buy' if req['action'] == 'buy' else 'Sell'} {req['shares']}x @ €{req['price']:.2f}"
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
        # (Only when advancing: while a candle is forming the timestamp stays put on purpose.)
        if advance and new_ts == timestamp:
            logger.info("Session ended (end of data at %s)", new_ts)
            log_session_event("session-finish", market_time(new_ts, n_steps, n_steps), cashflow, company, session_id)
            return (new_ts, fig, True, True, session_start_time, None) + sent_with_chart(new_ts, n_steps)

        logger.debug("ok new_ts=%s step=%s/%s", new_ts, new_step, n_steps)
        return ((new_ts, fig, no_update, no_update, session_start_time, (new_step if next_graph else no_update))
                + sent_with_chart(new_ts, new_step))

    except Exception as e:
        logger.exception("Error in update_graph: %s", e)
        return (no_update,) * 6 + _NOTHING_ELSE


# Nothing for the 5 values sent with the chart (timer ... shown-reminders)
_NOTHING_ELSE = (no_update,) * 5


def _news_clock(timestamp, step, n_steps, notif_offset, session_id):
    """[session, articles appeared, articles appeared incl. the 'warn me early' days].
    Changes only when a new article appears (or a new session starts), which is when
    the news list and the news pop-ups need to look again."""
    try:
        news_df = get_news_dataframe()
        index = get_market_dataframe().index
        now = now_position(index, timestamp, step, n_steps)
        ahead = now_position(index, timestamp, step, n_steps, candles_ahead=int(notif_offset or 0))
        return [session_id, appeared_count(news_df, index, n_steps, now), appeared_count(news_df, index, n_steps, ahead)]
    except Exception as e:
        logger.debug("Could not count the news that appeared: %s", e)
        return None


@callback(
    Output('revenue-graph', 'figure'),
    # A new simulated year (sent by update_graph): revenue data is yearly
    Input('revenue-year', 'data'),
    Input('company-selector', 'value'),
    State('timestamp', 'data'),
    State("companies", "data"),
    Input('color-scheme-store', 'data'),
)
def update_revenue(year, company, timestamp, companies, color_scheme):
    try:
        if companies[company]['activity'] == "Indice":
            return no_update

        ts = pd.to_datetime(timestamp)

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
            template='plotly_dark' if color_scheme == 'dark' else 'plotly_white',
        )

        return fig

    except Exception as e:
        logger.error("Error while drawing the revenue chart: %s", e)
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


