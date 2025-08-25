from dash import Output, Input, State, callback, no_update
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
    """Show/hide positive/negative news inputs depending on generation mode.

    Args:
        mode (str): 'random' or other modes.
        children: Existing children (unused; only triggers re-render).

    Returns:
        dict: CSS style dict controlling visibility.
    """
    if mode == 'random':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


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

    Input('generate-news', 'n_clicks'),
    prevent_initial_call=True
)
def on_start_button_clicked(companies, api_key, alpha, alpha_day_interval, delta, generation_mode,
                            nbr_positive_news, nbr_negative_news, n):
    """Generate news for each company and notify the user.

    Args:
        companies (dict): Companies metadata.
        api_key (str): API key for news generation service.
        alpha (float): Minimum percent market variation to place a news.
        alpha_day_interval (int): Days between points used to compute percent change.
        delta (int): Day shift for positioning news.
        generation_mode (str): 'rand' or 'linear'.
        nbr_positive_news (int): Number of positive news to generate.
        nbr_negative_news (int): Number of negative news to generate.
        n (int): Clicks on generate button.

    Returns:
        tuple: (notification component, False to reset loading state)
    """



    if n is None:
        raise PreventUpdate
    try:
        # Get the news position (timestamp) for all the companies
        news_position = get_news_position_for_companies(companies, generation_mode, nbr_positive_news, nbr_negative_news,
                                                        alpha, alpha_day_interval, delta)

        # Create the news for all the companies
        create_news_for_companies(companies, news_position, api_key)

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
            message=f"Error while generating news! it may be due to the API key or the parameters",
        ), False


@callback(
    Output("generate-news", "loading", allow_duplicate=True),
    Input("generate-news", "n_clicks"),
    prevent_initial_call=True
)
def update_loading(n):
    """Set the generate button loading state to True on click."""
    if n is None:
        raise PreventUpdate

    return True


@callback(
    Output("news-select-company", "data"),
    Input("settings-tabs", "value"),
    Input("companies", "data"),
)
def update_options_news_companies(tabs, companies):
    """Build options for the company dropdown used in news tab.

    Args:
        tabs (str): Current tab id (unused; triggers refresh).
        companies (dict): Companies list.

    Returns:
        list[dict]: Options for dmc.Select-like component.
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
    prevent_initial_call=True
)
def update_graph_news(company, alpha, alpha_day_interval, delta, mode, nbr_positive_news, nbr_negative_news):
    """Render the news-position preview chart for a selected company.

    Args:
        company (str): Company ticker.
        alpha (float): Alpha value for detection.
        alpha_day_interval (int): Interval for computing change.
        delta (int): Shift applied to positions.
        mode (str): 'linear' or 'random'.
        nbr_positive_news (int): Count of positive news when random mode.
        nbr_negative_news (int): Count of negative news when random mode.

    Returns:
        plotly.graph_objs.Figure|no_update: Preview figure or no_update on error.
    """
    if company is None:
        return no_update
    try:
        df = get_generated_data()[company]

        if mode == "linear":
            news_position = get_news_position_lin(df, alpha, alpha_day_interval, delta)
        else:
            news_position = get_news_position_rand(df, nbr_positive_news, nbr_negative_news, alpha, alpha_day_interval, delta)

        fig = display_chart(df, company, news_position)
        return fig

    except Exception as e:
        print("Error while updating the news graph :", e)
        return no_update


