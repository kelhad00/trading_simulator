import os

from dash import Output, Input, State, callback, no_update
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

from trade.utils.news_generation.news_creation import get_news_position_for_companies, create_news_for_companies, \
    get_news_position_lin, get_news_position_rand
from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.news_generation.display import display_chart


@callback(
    Output('nbr-news-container', 'style'),
    Output('top-k-container', 'style'),
    Input('input-generation-mode', 'value'),
)
def update_display_container_nbr_news(mode):
    """
    Switch the display of inputs depending on the generation mode:
    - random mode: show nbr positive/negative inputs
    - linear mode: show top-k input
    """
    if mode == 'random':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Output("generate-news", "loading"),

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

    Input('generate-news', 'n_clicks'),
    prevent_initial_call=True
)
def on_start_button_clicked(companies, api_key, alpha, alpha_day_interval, delta, generation_mode,
                            nbr_positive_news, nbr_negative_news, top_k, search, n):
    """
    Generate news for all the companies
    Args:
        companies: The list of companies
        api_key: The API key
        alpha:  the minimum percentage of market variation to place a news
        alpha_day_interval: the number of days between the two days used to calculate the percentage change
        delta: the number of days to shift the news position
        generation_mode: The generation mode (rand or linear)
        nbr_positive_news: The number of positive news
        nbr_negative_news: The number of negative news
        n: The number of clicks on the button
    Returns:
        A notification to inform the user when the generation is complete
        reset loading state (False)
    """
    if n is None:
        raise PreventUpdate
    try:
        # Get the news position (timestamp) for all the companies
        news_position = get_news_position_for_companies(companies, generation_mode, nbr_positive_news, nbr_negative_news,
                                                        alpha, alpha_day_interval, delta, k=top_k or 0)

        lang = "en" if (search and "lang=en" in search) else "fr"

        # Use the UI input URL if provided, otherwise fall back to the .env value
        effective_url = (api_key or "").strip() or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")

        # Create the news for all the companies
        create_news_for_companies(companies, news_position, lang, effective_url)

        return dmc.Notification(
            id="notification-news-generated",
            title="News",
            action="show",
            color="green",
            message=f"Generation complete !",
        ), False
    except Exception as e:
        print("Error while generating news :", e)
        return dmc.Notification(
            id="notification-news-generated",
            title="Error",
            action="show",
            color="red",
            message=f"Error while generating news! It may be due to the Ollama URL, the model, or the parameters.",
        ), False


@callback(
    Output("generate-news", "loading", allow_duplicate=True),
    Input("generate-news", "n_clicks"),
    prevent_initial_call=True
)
def update_loading(n):
    """
    Set the loading state to True when the button is clicked
    """
    if n is None:
        raise PreventUpdate

    return True


@callback(
    Output("news-select-company", "data"),
    Input("settings-tabs", "value"),
    Input("companies", "data"),
)
def update_options_news_companies(tabs, companies):
    """
    Update the options for the news select company dropdown
    Args:
        tabs: The tab selected (only to trigger the callback)
        companies: The list of companies
    Returns:
        The options for the dropdown
    """

    options = [{"label": company["label"], "value": stock} for stock, company in companies.items() if company["got_charts"]]
    return options

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
    prevent_initial_call=True
)
def update_graph_news(company, alpha, alpha_day_interval, delta, mode, nbr_positive_news, nbr_negative_news, top_k):
    """
    Update the news graph
    """
    if not company or alpha is None or alpha_day_interval is None or delta is None:
        raise PreventUpdate
    try:
        df = get_generated_data()[company]

        if mode == "linear":
            news_position = get_news_position_lin(df, alpha, alpha_day_interval, delta, k=top_k or 0)
        else:
            news_position = get_news_position_rand(df, nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta)

        fig = display_chart(df, company, news_position)
        return fig

    except Exception as e:
        print("Error while updating the news graph :", e)
        return no_update


