import os

from dash import Output, Input, State, callback, no_update
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

from trade.utils.news_generation.news_creation import (
    get_news_position_for_companies, create_news_for_companies,
    get_news_position_lin, get_news_position_rand, get_news_position_manual,
)
from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.news_generation.display import display_chart
from trade.locales import translations as tls


def _lang(search):
    return "en" if (search and "lang=en" in search) else "fr"


# ── Mode visibility ───────────────────────────────────────────────────────────

@callback(
    Output('nbr-news-container', 'style'),
    Output('top-k-container', 'style'),
    Output('manual-section', 'style'),
    Input('input-generation-mode', 'value'),
)
def update_display_container_nbr_news(mode):
    if mode == 'random':
        return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
    elif mode == 'linear':
        return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
    else:  # manual
        return {'display': 'none'}, {'display': 'none'}, {'display': 'flex'}


# ── Generate news ─────────────────────────────────────────────────────────────

@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Output("generate-news", "loading"),
    Output("manual-positions-store", "data", allow_duplicate=True),

    State('companies', 'data'),
    State('input-api-key', 'value'),
    State('input-alpha', 'value'),
    State('input-alpha-day-interval', 'value'),
    State('input-delta', 'value'),
    State('input-generation-mode', 'value'),
    State('input-nbr-positive-news', 'value'),
    State('input-nbr-negative-news', 'value'),
    State('input-top-k', 'value'),
    State('url', 'search'),
    State('manual-positions-store', 'data'),

    Input('generate-news', 'n_clicks'),
    prevent_initial_call=True
)
def on_start_button_clicked(companies, api_key, alpha, alpha_day_interval, delta, generation_mode,
                            nbr_positive_news, nbr_negative_news, top_k, search, manual_positions, n):
    if n is None:
        raise PreventUpdate
    try:
        news_position = get_news_position_for_companies(
            companies, generation_mode, nbr_positive_news, nbr_negative_news,
            alpha, alpha_day_interval, delta,
            k=top_k or 0,
            manual_positions=manual_positions or {},
        )

        lang = _lang(search)
        effective_url = (api_key or "").strip() or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        create_news_for_companies(companies, news_position, lang, effective_url)

        return dmc.Notification(
            id="notification-news-generated",
            title="News",
            action="show",
            color="green",
            message="Generation complete!",
        ), False, {}  # clear manual positions after successful generation

    except Exception as e:
        print("Error while generating news:", e)
        return dmc.Notification(
            id="notification-news-generated",
            title="Error",
            action="show",
            color="red",
            message="Error while generating news! It may be due to the Ollama URL, the model, or the parameters.",
        ), False, no_update  # keep manual positions on failure


@callback(
    Output("generate-news", "loading", allow_duplicate=True),
    Input("generate-news", "n_clicks"),
    prevent_initial_call=True
)
def update_loading(n):
    if n is None:
        raise PreventUpdate
    return True


# ── Company dropdown options ──────────────────────────────────────────────────

@callback(
    Output("news-select-company", "data"),
    Input("settings-tabs", "value"),
    Input("companies", "data"),
)
def update_options_news_companies(tabs, companies):
    return [
        {"label": company["label"], "value": stock}
        for stock, company in companies.items()
        if company["got_charts"]
    ]


# ── Preview chart ─────────────────────────────────────────────────────────────

@callback(
    Output("news-chart", "figure"),
    Input("news-select-company", "value"),
    Input("input-alpha", "value"),
    Input("input-alpha-day-interval", "value"),
    Input("input-delta", "value"),
    Input('input-generation-mode', 'value'),
    Input('input-nbr-positive-news', 'value'),
    Input('input-nbr-negative-news', 'value'),
    Input('input-top-k', 'value'),
    Input('manual-positions-store', 'data'),
    prevent_initial_call=True
)
def update_graph_news(company, alpha, alpha_day_interval, delta, mode,
                      nbr_positive_news, nbr_negative_news, top_k, manual_store):
    if not company:
        raise PreventUpdate
    try:
        df = get_generated_data()[company]

        if mode == "manual":
            company_data = (manual_store or {}).get(company, {"positive": [], "negative": []})
            news_position = get_news_position_manual(
                df,
                company_data.get("positive", []),
                company_data.get("negative", []),
            )
        elif mode == "linear":
            if alpha is None or alpha_day_interval is None or delta is None:
                raise PreventUpdate
            news_position = get_news_position_lin(df, alpha, alpha_day_interval, delta, k=top_k or 0)
        else:
            if alpha is None or alpha_day_interval is None or delta is None:
                raise PreventUpdate
            news_position = get_news_position_rand(df, nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta)

        return display_chart(df, company, news_position)

    except PreventUpdate:
        raise
    except Exception as e:
        print("Error while updating the news graph:", e)
        return no_update


# ── Hover-to-aim indicator ────────────────────────────────────────────────────

@callback(
    Output("manual-hover-text", "children"),
    Input("news-chart", "hoverData"),
    State("input-generation-mode", "value"),
    State("input-news-sentiment", "value"),
    State("url", "search"),
    prevent_initial_call=True
)
def update_hover_indicator(hover_data, mode, sentiment, search):
    if mode != "manual":
        raise PreventUpdate
    tm = tls[_lang(search)]["settings"]["news"]["manual"]
    if not hover_data:
        return tm["hover-text-idle"]
    date = str(hover_data['points'][0]['x'])[:10]
    sentiment_label = tm["sentiment-positive"] if sentiment == "positive" else tm["sentiment-negative"]
    return tm["hover-text-active"].format(sentiment=sentiment_label.lower(), date=date)


# ── Chart click → store ───────────────────────────────────────────────────────

@callback(
    Output("manual-positions-store", "data"),
    Input("news-chart", "clickData"),
    State("input-news-sentiment", "value"),
    State("news-select-company", "value"),
    State("input-generation-mode", "value"),
    State("manual-positions-store", "data"),
    prevent_initial_call=True
)
def handle_chart_click(click_data, sentiment, company, mode, store):
    if mode != "manual" or not click_data or not company:
        raise PreventUpdate

    clicked_date = str(click_data['points'][0]['x'])[:10]
    store = dict(store or {})

    if company not in store:
        store[company] = {"positive": [], "negative": []}
    else:
        store[company] = {
            "positive": list(store[company].get("positive", [])),
            "negative": list(store[company].get("negative", [])),
        }

    other = "negative" if sentiment == "positive" else "positive"

    if clicked_date in store[company][sentiment]:
        # Toggle off — same point clicked again
        store[company][sentiment].remove(clicked_date)
    elif clicked_date in store[company][other]:
        # Move from opposite sentiment to the selected one
        store[company][other].remove(clicked_date)
        store[company][sentiment].append(clicked_date)
    else:
        store[company][sentiment].append(clicked_date)

    return store


# ── Date picker backup → store ────────────────────────────────────────────────

@callback(
    Output("manual-positions-store", "data", allow_duplicate=True),
    Input("add-manual-date", "n_clicks"),
    State("input-manual-date", "value"),
    State("input-news-sentiment", "value"),
    State("news-select-company", "value"),
    State("manual-positions-store", "data"),
    prevent_initial_call=True
)
def handle_datepicker_add(n, date_value, sentiment, company, store):
    if not n or not date_value or not company:
        raise PreventUpdate

    date_str = str(date_value)[:10]
    store = dict(store or {})

    if company not in store:
        store[company] = {"positive": [], "negative": []}
    else:
        store[company] = {
            "positive": list(store[company].get("positive", [])),
            "negative": list(store[company].get("negative", [])),
        }

    other = "negative" if sentiment == "positive" else "positive"
    if date_str in store[company][other]:
        store[company][other].remove(date_str)
    if date_str not in store[company][sentiment]:
        store[company][sentiment].append(date_str)

    return store


# ── Position counter + flagged notice ────────────────────────────────────────

@callback(
    Output("manual-position-counter", "children"),
    Output("manual-flagged-notice", "children"),
    Input("manual-positions-store", "data"),
    Input("news-select-company", "value"),
    Input("input-generation-mode", "value"),
    State("url", "search"),
)
def update_manual_counter_and_notice(store, company, mode, search):
    tm = tls[_lang(search)]["settings"]["news"]["manual"]
    store = store or {}

    # Counter for the currently selected company
    if company and company in store:
        pos = len(store[company].get("positive", []))
        neg = len(store[company].get("negative", []))
        counter = tm["counter"].format(positive=pos, negative=neg) if (pos or neg) else tm["counter-empty"]
    else:
        counter = tm["counter-empty"]

    # Flagged notice shown in random/linear mode
    flagged = sum(
        1 for d in store.values()
        if d.get("positive") or d.get("negative")
    )
    if flagged > 0 and mode != "manual":
        template = tm["flagged-notice"] if flagged == 1 else tm["flagged-notice-plural"]
        notice = dmc.Alert(
            template.format(count=flagged),
            color="blue",
            variant="light",
        )
    else:
        notice = None

    return counter, notice


# ── Clear one company's manual positions ──────────────────────────────────────

@callback(
    Output("manual-positions-store", "data", allow_duplicate=True),
    Input("clear-manual-company", "n_clicks"),
    State("news-select-company", "value"),
    State("manual-positions-store", "data"),
    prevent_initial_call=True
)
def clear_company_manual_positions(n, company, store):
    if not n or not company:
        raise PreventUpdate
    store = dict(store or {})
    store.pop(company, None)
    return store


# ── Date picker range (min/max) from market data ──────────────────────────────

@callback(
    Output("input-manual-date", "minDate"),
    Output("input-manual-date", "maxDate"),
    Input("news-select-company", "value"),
)
def update_datepicker_range(company):
    if not company:
        raise PreventUpdate
    try:
        df = get_generated_data()[company]
        return str(df.index[0])[:10], str(df.index[-1])[:10]
    except Exception:
        raise PreventUpdate
