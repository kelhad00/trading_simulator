from dash import Output, Input, State, html, callback, no_update
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from trade.utils.news_generation.news_creation import get_news_position_for_companies, create_news_for_companies, \
    get_news_position_lin, get_news_position_rand
from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.news_generation.display import display_chart


@callback(
    Output('nbr-news-container', 'style'),
    Input('input-generation-mode', 'value'),
    State('nbr-news-container', 'children')
)
def update_display_container_nbr_news(mode, children):
    """
    Switch the display of inputs (number of positive and negative news) depending on the generation mode
    """
    if mode == 'random':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@callback(
    Output('notifications', 'children', allow_duplicate=True),

    State('companies', 'data'),
    State('activities', 'data'),
    State('input-api-key', 'value'),
    State('input-alpha', 'value'),
    State('input-alpha-day-interval', 'value'),
    State('input-delta', 'value'),
    State('input-generation-mode', 'value'),
    State('input-nbr-positive-news', 'value'),
    State('input-nbr-negative-news', 'value'),

    Input('generate-news', 'n_clicks'),
    prevent_initial_call=True
)
def on_start_button_clicked(companies, activities, api_key, alpha, alpha_day_interval, delta, generation_mode,
                            nbr_positive_news, nbr_negative_news, n):
    """
    Generate news for all the companies
    Args:
        companies: The list of companies
        activities: The activities
        api_key: The API key
        alpha: The alpha value
        alpha_day_interval: The alpha day interval
        delta: The delta value
        generation_mode: The generation mode
        nbr_positive_news: The number of positive news
        nbr_negative_news: The number of negative news
        n: The number of clicks on the button
    Returns:
        A notification to inform the user when the generation is complete
    """
    if n is None:
        raise PreventUpdate

    # TODO : Créer un visuel de chargement

    # Get the news position (timestamp) for all the companies
    news_position = get_news_position_for_companies(companies, generation_mode, nbr_positive_news, nbr_negative_news,
                                                    alpha, alpha_day_interval, delta)

    # Create the news for all the companies
    create_news_for_companies(companies, activities, news_position, api_key)

    return dmc.Notification(
        id="notification-news-generated",
        title="News",
        action="show",
        color="green",
        message=f"Generation complete !",
    )



@callback(
    Output("news-select-company", "data"),
    Input("settings-tabs", "value"),
    Input("companies", "data"),
)
def update_options_news_companies(tabs, companies):

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
    prevent_initial_call=True
)
def update_graph_news(company, alpha, alpha_day_interval, delta, mode, nbr_positive_news, nbr_negative_news):
    try:
        df = get_generated_data()[company]

        if mode == "linear":
            news_position = get_news_position_lin(df, alpha, alpha_day_interval, delta)
        else:
            news_position = get_news_position_rand(df, nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta)

        fig = display_chart(df, company, news_position)
        return fig

    except Exception as e:
        print(e)
        return no_update


