import os
import threading

import pandas as pd
import dash_mantine_components as dmc

from dash import callback, Input, Output, State, ALL, no_update, dcc, page_registry
from dash.exceptions import PreventUpdate

from trade.utils.market import get_first_timestamp
from trade.utils.ordinal import ordinal
from trade.utils.settings.create_market_data import (
    bull_trend, bear_trend, flat_trend,
    export_generated_data, get_generated_data,
    generate_synthetic_ohlcv, inject_pattern,
)
from trade.utils.settings.display import display_chart
from trade.utils.settings.data_handler import scale_market_data, load_data, get_data_size
from trade.layouts.settings.sections.charts import timeline_item
from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.news_generation.news_creation import (
    get_news_position_for_companies, create_news_for_companies,
)


# ── Crash-point slider visibility ────────────────────────────────────────────

@callback(
    Output("crash-point-container", "style"),
    Input("select-curve-profile", "value"),
)
def toggle_crash_point_visibility(profile):
    """Show the crash-point slider only when the crash profile is selected."""
    if profile == "crash":
        return {"display": "block"}
    return {"display": "none"}


# ── Disable segment-only controls for synthetic profiles ─────────────────────

_INACTIVE = {"opacity": "0.35", "pointerEvents": "none", "userSelect": "none"}
_ACTIVE = {}


@callback(
    Output("slider-alpha", "disabled"),
    Output("alpha-section", "style"),
    Output("timeline-radio-section", "style"),
    Input("select-curve-profile", "value"),
)
def toggle_segment_controls(profile):
    """
    Disable controls that are irrelevant for synthetic profiles:
      - slider-alpha      : used only by bull_trend / bear_trend searches
      - timeline radios   : bull/bear/flat choices are ignored; only the
                            *count* of trends (number-trends) still matters
                            as a period multiplier, so number-trends stays on.
    """
    if not profile or profile == "segments":
        return False, _ACTIVE, _ACTIVE
    return True, _INACTIVE, _INACTIVE


# ── Chart generation (preview in modal) ──────────────────────────────────────

@callback(
    Output("modal-generated-charts-container", "children"),
    Output("figures", "data"),
    Input("slider-alpha", "value"),
    Input("slider-length", "value"),
    Input("slider-start", "value"),
    Input({"type": "timeline-radio", "index": ALL}, "value"),
    Input({"type": "timeline-pattern", "index": ALL}, "value"),
    Input("modal-select-companies", "value"),
    Input("select-curve-profile", "value"),
    Input("slider-noise", "value"),
    Input("slider-crash-point", "value"),
    prevent_initial_call=True,
)
def generate_new_charts(
    alpha, length, start_value,
    radio_trends, pattern_trends, companies,
    curve_profile, noise_level, crash_point,
    start_date=dlt.start_date,
):
    """
    Generate preview charts for the selected companies.

    When curve_profile is not 'segments', synthetic OHLCV data is produced
    directly from the chosen growth curve.  Otherwise the existing segment-based
    approach (extracting bull/bear/flat windows from real market data) is used.
    """
    if not companies:
        raise PreventUpdate

    try:
        df_existing = get_generated_data()
        first_timestamp = get_first_timestamp(df_existing)
    except Exception:
        first_timestamp = start_date

    # ── Synthetic curve generation ────────────────────────────────────────────
    if curve_profile and curve_profile != "segments":
        try:
            nb_segments = max(len(radio_trends), 1)
            n_periods = max(int(length or 100) * nb_segments, 2)
            noise_pct = float(noise_level) if noise_level is not None else 10.0
            crash_pct = float(crash_point) if crash_point is not None else 70.0

            dataframes = []
            figures = []

            for company in companies:
                df = generate_synthetic_ohlcv(
                    n_periods=n_periods,
                    profile=curve_profile,
                    noise_pct=noise_pct,
                    start_value=float(start_value) if start_value else 250.0,
                    start_date=first_timestamp,
                    crash_point_pct=crash_pct,
                )
                df_indexed = df.set_index("Date")
                fig = display_chart(df_indexed, 0, df_indexed.shape[0], company)
                figures.append(fig)
                dataframes.append(df.to_dict())  # keep Date as column for export

            children = [dcc.Graph(figure=fig) for fig in figures]
            return children, dataframes

        except Exception as e:
            print("Error while generating synthetic charts:", e)
            return no_update, no_update

    # ── Segment-based generation (original approach) ──────────────────────────
    if None in radio_trends:
        return no_update, no_update

    try:
        dataset = load_data(os.path.join(dlt.data_path, "CAC40.csv"))
        data_size = get_data_size(dataset)

        dataframes = []
        figures = []

        for company in companies:
            trends = []
            for trend_val in radio_trends:
                if trend_val == "bull":
                    trends.append(bull_trend(dataset, data_size, alpha, length))
                elif trend_val == "bear":
                    trends.append(bear_trend(dataset, data_size, alpha, length))
                else:
                    trends.append(flat_trend(dataset, data_size, 20, length))

            data_list = [
                dataset[t: t + length].reset_index(drop=True)
                for t in trends
            ]

            for i, segment in enumerate(data_list):
                if i == 0:
                    data_list[0] = scale_market_data(segment, start_value)
                else:
                    data_list[i] = scale_market_data(
                        segment, data_list[i - 1].iloc[-1]["Close"]
                    )

            # Inject per-segment patterns (skip "none" and unset values)
            for i, pattern_type in enumerate(pattern_trends or []):
                if i < len(data_list) and pattern_type and pattern_type != "none":
                    data_list[i] = inject_pattern(data_list[i], pattern_type)

            final_chart = pd.concat(data_list).reset_index(drop=True)
            final_chart["Date"] = pd.date_range(
                start=first_timestamp, periods=final_chart.shape[0], freq="D"
            )

            fig = display_chart(final_chart, 0, final_chart.shape[0], company)
            figures.append(fig)
            dataframes.append(final_chart.to_dict())

        children = [dcc.Graph(figure=fig) for fig in figures]
        return children, dataframes

    except Exception as e:
        print("Error while generating charts:", e)
        return no_update, no_update


# ── Export confirmed charts to CSV ────────────────────────────────────────────

def _auto_generate_news(companies_subset, mode, nbr_pos, nbr_neg, alpha, interval, delta, lang, key):
    """Run news generation in a background thread so the UI is not blocked."""
    try:
        positions = get_news_position_for_companies(
            companies_subset, mode, nbr_pos, nbr_neg, alpha, interval, delta
        )
        create_news_for_companies(companies_subset, positions, lang, key)
        print("Auto news regeneration complete for: " + ", ".join(companies_subset.keys()))
    except Exception as e:
        print("Auto news regeneration failed:", e)


@callback(
    Output("figures", "data", allow_duplicate=True),
    Output("modal", "opened", allow_duplicate=True),
    Output({"type": "timeline-radio", "index": ALL}, "value"),
    Output("companies", "data", allow_duplicate=True),
    Output("notifications", "children", allow_duplicate=True),

    Input("generate-button", "n_clicks"),
    State("figures", "data"),
    State("modal-select-companies", "value"),
    State("number-trends", "value"),
    State("companies", "data"),
    State("select-curve-profile", "value"),
    State("input-api-key", "value"),
    State("input-alpha", "value"),
    State("input-alpha-day-interval", "value"),
    State("input-delta", "value"),
    State("input-generation-mode", "value"),
    State("input-nbr-positive-news", "value"),
    State("input-nbr-negative-news", "value"),
    State("url", "search"),
    prevent_initial_call=True,
)
def export_generated_charts(n, datas, companies_selected, nb_radio, companies, curve_profile,
                             api_key, alpha, alpha_day_interval, delta, generation_mode,
                             nbr_positive_news, nbr_negative_news, search):
    """
    Export the generated charts to generated_data.csv when the generate button is clicked,
    then automatically regenerate news for those companies in a background thread.
    """
    if datas is None or datas == []:
        raise PreventUpdate

    for index, data in enumerate(datas):
        company = companies_selected[index]
        df = pd.DataFrame.from_dict(data)
        export_generated_data(df, company)
        companies[company]["got_charts"] = True
        companies[company]["curve_profile"] = curve_profile

    # Build subset of only the companies whose charts were just confirmed
    companies_subset = {c: companies[c] for c in companies_selected}

    effective_key = (api_key or "").strip() or os.environ.get("GROQ_API_KEY", "")
    lang = "en" if (search and "lang=en" in search) else "fr"

    thread = threading.Thread(
        target=_auto_generate_news,
        args=(
            companies_subset,
            generation_mode or "random",
            nbr_positive_news or 2,
            nbr_negative_news or 2,
            alpha or 0.5,
            alpha_day_interval or 3,
            delta or 0,
            lang,
            effective_key,
        ),
        daemon=True,
    )
    thread.start()

    notification = dmc.Notification(
        id="notif-news-auto",
        title="News",
        action="show",
        color="blue",
        message="News generation started for " + ", ".join(companies_selected) + ". This runs in the background.",
    )

    return list(), False, [None] * nb_radio, companies, notification


# ── Select-all shortcut ───────────────────────────────────────────────────────

@callback(
    Output("modal-select-companies", "value", allow_duplicate=True),
    Input("select-all-stocks", "n_clicks"),
    State("companies", "data"),
    prevent_initial_call=True,
)
def select_all_stocks(n, companies):
    return list(companies.keys())


# ── Timeline size update ──────────────────────────────────────────────────────

@callback(
    Output("timeline", "children"),
    Input("number-trends", "value"),
    State("timeline", "children"),
    prevent_initial_call=True,
)
def update_timeline(nb, children, min=1, max=5):
    """Add or remove timeline radio items to match the requested trend count."""
    if nb == "" or nb is None or nb < min or nb > max:
        return no_update

    try:
        while len(children) != nb:
            if len(children) < nb:
                children.append(
                    timeline_item(
                        id="timeline",
                        index=len(children) + 1,
                        title=(
                            f"{ordinal(len(children) + 1, page_registry['lang'])} "
                            f"{tls[page_registry['lang']]['settings']['charts']['radio']['title']}"
                        ),
                    )
                )
            else:
                children.pop()

        return children

    except Exception as e:
        print("Error:", e)
        return no_update


@callback(
    Output("timeline", "active"),
    Input({"type": "timeline-radio", "index": ALL}, "value"),
)
def update_timeline_active(values):
    """Advance the timeline highlight to the last completed item."""
    if None in values:
        return values.index(None) - 1
    return len(values) - 1
