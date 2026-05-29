import os
import threading

import numpy as np
import pandas as pd
import dash_mantine_components as dmc

from dash import callback, Input, Output, State, ALL, no_update, dcc, ctx
from dash.exceptions import PreventUpdate

from trade.utils.market import get_first_timestamp
from trade.utils.ordinal import ordinal
from trade.utils.settings.create_market_data import (
    bull_trend, bear_trend, flat_trend,
    export_generated_data, get_generated_data,
    apply_event_overlay,
)
from trade.utils.settings.display import display_chart
from trade.utils.settings.data_handler import (
    scale_market_data, normalize_to_volatility,
    load_data, get_data_size, get_pattern_file_excluding,
)
from trade.layouts.settings.sections.charts import timeline_item
from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.news_generation.news_creation import (
    get_news_position_for_companies, create_news_for_companies,
)
import trade.callbacks.settings.stocks as stocks_callbacks


# ── Step 1: pick CAC40 windows when trends/params change ─────────────────────
#
# None radios are treated as 'flat' — those segments may be overridden by a
# pattern file chosen in step 2, so the stored index is just a safe fallback.

@callback(
    Output("base-figures", "data"),
    Input("slider-alpha", "value"),
    Input({"type": "timeline-length", "index": ALL}, "value"),
    Input("slider-start", "value"),
    Input({"type": "timeline-radio", "index": ALL}, "value"),
    Input("modal-select-companies", "value"),
    prevent_initial_call=True,
)
def generate_base_segments(alpha, segment_lengths, start_value, radio_trends, companies,
                            start_date=dlt.start_date):
    if not companies:
        raise PreventUpdate

    try:
        df_existing = get_generated_data()
        first_timestamp = str(get_first_timestamp(df_existing))
    except Exception:
        first_timestamp = str(start_date)

    try:
        dataset   = load_data(os.path.join(dlt.data_path, "CAC40.csv"))
        data_size = get_data_size(dataset)

        company_data = []
        for company in companies:
            indices = []
            for i, trend_val in enumerate(radio_trends):
                length_i = int(segment_lengths[i]) if i < len(segment_lengths) and segment_lengths[i] else 100
                tv = trend_val or "flat"
                if tv == "bull":
                    indices.append(bull_trend(dataset, data_size, alpha, length_i))
                elif tv == "bear":
                    indices.append(bear_trend(dataset, data_size, alpha, length_i))
                else:
                    indices.append(flat_trend(dataset, data_size, 20, length_i))
            company_data.append({"company": company, "indices": indices})

        lengths = [int(segment_lengths[i]) if i < len(segment_lengths) and segment_lengths[i] else 100
                   for i in range(len(radio_trends))]

        return {
            "company_data":    company_data,
            "segment_lengths": lengths,
            "start_value":     float(start_value) if start_value else 250.0,
            "first_timestamp": first_timestamp,
        }

    except Exception as e:
        print("Error generating base segments:", e)
        return no_update


# ── Step 2: choose pattern files (no-repeat per company) ─────────────────────
#
# Fires when pattern dropdowns change OR when base-figures resets (new windows).
# Picking files here — not in the render step — keeps the chosen files stable
# when only event controls change.

@callback(
    Output("pattern-files", "data"),
    Input({"type": "timeline-pattern", "index": ALL}, "value"),
    Input("base-figures", "data"),
    State("pattern-files", "data"),
    prevent_initial_call=True,
)
def select_pattern_files(pattern_trends, base_data, prev_files):
    if not base_data:
        raise PreventUpdate

    # When base-figures triggered, all windows changed → re-pick every file.
    # When only a pattern dropdown changed, keep existing files for segments
    # whose pattern type is unchanged so one segment's change doesn't re-roll others.
    base_changed = ctx.triggered_id == "base-figures"

    prev_types  = (prev_files or {}).get('pattern_types', [])
    prev_lookup = {}
    if prev_files and not base_changed:
        for entry in (prev_files.get('company_data') or []):
            prev_lookup[entry['company']] = entry['segment_files']

    company_data = []
    for entry in base_data["company_data"]:
        company    = entry["company"]
        prev_segs  = prev_lookup.get(company, [])
        used_paths = set()
        segment_files = []

        for seg_i, pattern_type in enumerate(pattern_trends or []):
            if pattern_type and pattern_type != "none":
                prev_type = prev_types[seg_i] if seg_i < len(prev_types) else None
                prev_path = prev_segs[seg_i]  if seg_i < len(prev_segs)  else None

                if not base_changed and prev_type == pattern_type and prev_path:
                    # Same type, same base data → keep the already-chosen file
                    path = prev_path
                else:
                    path = get_pattern_file_excluding(pattern_type, used_paths)

                if path:
                    used_paths.add(path)
                segment_files.append(path)
            else:
                segment_files.append(None)

        company_data.append({
            "company":       company,
            "segment_files": segment_files,
        })

    return {
        "company_data":  company_data,
        "pattern_types": list(pattern_trends or []),
    }


# ── Event overlay: show/hide position + magnitude sliders ────────────────────

@callback(
    Output("event-params-container", "style"),
    Input("select-event-type", "value"),
)
def toggle_event_params(event_type):
    if event_type and event_type != "none":
        return {"display": "block"}
    return {"display": "none"}


# ── Warn when the event position overlaps a pattern segment ───────────────────

@callback(
    Output("event-overlap-warning", "style"),
    Output("event-overlap-warning", "children"),
    Input("select-event-type", "value"),
    Input("slider-event-position", "value"),
    Input({"type": "timeline-length", "index": ALL}, "value"),
    Input({"type": "timeline-pattern", "index": ALL}, "value"),
    State("url", "search"),
)
def warn_event_pattern_overlap(event_type, event_position, segment_lengths, pattern_trends, search):
    hidden = {"display": "none"}

    if not event_type or event_type == "none":
        return hidden, ""
    if event_position is None or not pattern_trends or not segment_lengths:
        return hidden, ""

    lengths = [max(int(l or 100), 1) for l in segment_lengths]
    total_bars = sum(lengths)
    event_bar = int(total_bars * event_position / 100)

    seg_index = len(lengths) - 1
    cumulative = 0
    for i, l in enumerate(lengths):
        cumulative += l
        if event_bar < cumulative:
            seg_index = i
            break

    pattern_at_event = pattern_trends[seg_index] if seg_index < len(pattern_trends) else None

    if pattern_at_event and pattern_at_event != "none":
        lang = "en" if (search and "lang=en" in search) else "fr"
        name = pattern_at_event.replace("_", " ").title()
        template = tls[lang]["settings"]["charts"]["event"]["overlap-warning"]
        msg = template % (event_type, seg_index + 1, name)
        return {"display": "block"}, msg

    return hidden, ""


# ── Disable radio when a pattern is selected for that segment ─────────────────

_DISABLED_STYLE = {"opacity": "0.35", "pointerEvents": "none", "userSelect": "none"}

@callback(
    Output({"type": "timeline-radio-container", "index": ALL}, "style"),
    Output({"type": "timeline-length-container", "index": ALL}, "style"),
    Input({"type": "timeline-pattern", "index": ALL}, "value"),
)
def toggle_radio_on_pattern(pattern_values):
    styles = [
        _DISABLED_STYLE if (pv and pv != "none") else {}
        for pv in (pattern_values or [])
    ]
    return styles, styles


# ── Step 3: render chart from fixed windows + chosen pattern files ────────────
#
# base-figures is a State (not Input) so only pattern-files or event control
# changes trigger a re-render — no double-fire when base-figures updates.

def _format_bar_count(n):
    """Convert a bar count to a human-readable duration string."""
    years  = n // 252
    months = (n % 252) // 21
    parts  = []
    if years:  parts.append('%d yr%s'  % (years,  's' if years  > 1 else ''))
    if months: parts.append('%d mo'    % months)
    if parts:
        return '%d bars  (~%s of trading data)' % (n, ' '.join(parts))
    return '%d bars  (< 1 mo of trading data)' % n


@callback(
    Output("modal-generated-charts-container", "children"),
    Output("figures", "data"),
    Output("chart-bar-count", "children"),
    Input("pattern-files", "data"),
    Input("select-event-type", "value"),
    Input("slider-event-position", "value"),
    Input("slider-event-magnitude", "value"),
    State("base-figures", "data"),
    prevent_initial_call=True,
)
def apply_patterns_and_display(pattern_files, event_type, event_position, event_magnitude,
                                base_data):
    if not base_data:
        raise PreventUpdate

    try:
        dataset = load_data(os.path.join(dlt.data_path, "CAC40.csv"))

        segment_lengths = base_data["segment_lengths"]
        start_value     = base_data["start_value"]
        first_timestamp = base_data["first_timestamp"]

        # Build per-company file lookup: company → [path|None, ...]
        file_lookup = {}
        if pattern_files:
            for entry in pattern_files["company_data"]:
                file_lookup[entry["company"]] = entry["segment_files"]

        dataframes  = []
        figures     = []
        bar_count_str = ""

        # Fallback volatility: daily return std of the full CAC40 dataset
        global_vol = dataset['Close'].pct_change().std()

        for company_idx, entry in enumerate(base_data["company_data"]):
            company   = entry["company"]
            indices   = entry["indices"]
            seg_files = file_lookup.get(company, [None] * len(indices))

            # Compute target volatility from this company's CAC40 windows
            cac_returns = []
            for seg_i, (t, fp) in enumerate(zip(indices, seg_files)):
                if fp is None:
                    length_i = segment_lengths[seg_i] if seg_i < len(segment_lengths) else 100
                    window = dataset[t: t + length_i]
                    cac_returns.extend(window['Close'].pct_change().dropna().tolist())
            target_vol = float(np.std(cac_returns)) if len(cac_returns) >= 5 else global_vol

            data_list  = []
            prev_close = start_value

            for seg_i, (t, file_path) in enumerate(zip(indices, seg_files)):
                length_i = segment_lengths[seg_i] if seg_i < len(segment_lengths) else 100
                if file_path:
                    segment = normalize_to_volatility(
                        load_data(file_path), prev_close, target_vol
                    )
                else:
                    segment = scale_market_data(
                        dataset[t: t + length_i].reset_index(drop=True), prev_close
                    )

                data_list.append(segment)
                prev_close = segment.iloc[-1]["Close"]

            # Compute bar count from the first company (representative)
            if company_idx == 0:
                bar_count_str = _format_bar_count(sum(len(s) for s in data_list))

            final_chart = pd.concat(data_list).reset_index(drop=True)

            if event_type and event_type != "none":
                final_chart = apply_event_overlay(
                    final_chart,
                    event_type,
                    float(event_position)  if event_position  is not None else 50.0,
                    float(event_magnitude) if event_magnitude is not None else 40.0,
                )

            final_chart["Date"] = pd.date_range(
                start=first_timestamp, periods=final_chart.shape[0], freq="D"
            )

            fig = display_chart(final_chart, 0, final_chart.shape[0], company)
            figures.append(fig)
            dataframes.append(final_chart.to_dict())

        children = [dcc.Graph(figure=fig) for fig in figures]
        return children, dataframes, bar_count_str

    except Exception as e:
        print("Error applying patterns:", e)
        return no_update, no_update, no_update


# ── Export confirmed charts to CSV ────────────────────────────────────────────

def _auto_generate_news(companies_subset, mode, nbr_pos, nbr_neg, alpha, interval, delta, lang, base_url, k=0):
    """Run news generation in a background thread so the UI is not blocked."""
    try:
        positions = get_news_position_for_companies(
            companies_subset, mode, nbr_pos, nbr_neg, alpha, interval, delta, k=k
        )
        create_news_for_companies(companies_subset, positions, lang, base_url)
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
    State("input-api-key", "value"),
    State("input-alpha", "value"),
    State("input-alpha-day-interval", "value"),
    State("input-delta", "value"),
    State("input-generation-mode", "value"),
    State("input-nbr-positive-news", "value"),
    State("input-nbr-negative-news", "value"),
    State("input-top-k", "value"),
    State("url", "search"),
    prevent_initial_call=True,
)
def export_generated_charts(n, datas, companies_selected, nb_radio, companies,
                             api_key, alpha, alpha_day_interval, delta, generation_mode,
                             nbr_positive_news, nbr_negative_news, top_k, search):
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

    stocks_callbacks._cached_df_companies = None  # invalidate cache — CSV has changed

    # Build subset of only the companies whose charts were just confirmed
    companies_subset = {c: companies[c] for c in companies_selected}

    effective_url = (api_key or "").strip() or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
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
            effective_url,
            top_k or 0,
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
    State("url", "search"),
    prevent_initial_call=True,
)
def update_timeline(nb, children, search, min=1, max=5):
    """Add or remove timeline radio items to match the requested trend count."""
    if nb == "" or nb is None or nb < min or nb > max:
        return no_update

    lang = "en" if (search and "lang=en" in search) else "fr"

    try:
        while len(children) != nb:
            if len(children) < nb:
                children.append(
                    timeline_item(
                        id="timeline",
                        index=len(children) + 1,
                        title=(
                            f"{ordinal(len(children) + 1, lang)} "
                            f"{tls[lang]['settings']['charts']['radio']['title']}"
                        ),
                        lang=lang,
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
    Input({"type": "timeline-pattern", "index": ALL}, "value"),
)
def update_timeline_active(radio_values, pattern_values):
    """Advance the timeline highlight to the last completed item.
    A segment is complete when it has either a radio selection or a pattern chosen."""
    for i, (radio, pattern) in enumerate(zip(radio_values, pattern_values or [])):
        if radio is None and (not pattern or pattern == "none"):
            return max(0, i - 1)
    return len(radio_values) - 1
