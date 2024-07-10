from dash import callback, Output, Input, State, page_registry, ALL, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import pandas as pd

from trade.locales import translations as tls
from trade.components.table import create_table
from trade.utils.news import get_news_dataframe
from trade.utils.news_generation.news_creation import get_news_position_lin, get_news_position_rand, create_news
from trade.utils.market import get_market_dataframe


@callback(
    Output('news-table', 'children'),
    Input('periodic-updater', 'n_intervals'),
    Input('company-selector', 'value'),
    State('timestamp', 'data'),
)
def cb_update_news_table(n, company, timestamp, range=50, daily=True):
    """
    Function to display the latest news in the table from the timestamp
    Args:
        timestamp: The last timestamp
    Returns:
        The updated news table
    """

    try:
        news_df = get_news_dataframe()
    except FileNotFoundError:
        raise "The news.csv file was not generated."

    lang = page_registry['lang']

    # Format the news dataframe
    try:
        news_df = news_df.drop_duplicates(subset=['title'], keep='first') \
            .rename({'title': 'article'}, axis=1)
    except KeyError:  # Else, if news_df contains an article column
        try:
            news_df = news_df.drop_duplicates(subset=['article'], keep='first')
        except KeyError:  # news _df is not correctly formatted
            print('WARNING: The `news.csv` file must contain a `title` or `article` column.')
            raise PreventUpdate

    # Convert the date column and the timestamp to datetime
    news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True, format='mixed')
    timestamp = pd.to_datetime(timestamp).tz_localize(None)

    if daily:
        timestamp = timestamp + pd.Timedelta(days=1)  # get the date of the next day

    # Get the news before the timestamp
    nl = news_df.loc[news_df['date'] <= timestamp].sort_values(by='date', ascending=False).astype(str)

    #Display article and date columns
    nl = nl[['article', 'date']]
    nl = nl[:range]
    nl = nl.rename(columns={
        'date': tls[lang]['news-table']['date'],
        'article': tls[lang]['news-table']['article']
    })

    return dmc.Table(children=create_table(nl, id="news-lines"))



@callback(
    Output('news-container', 'style'),
    Output('description-title', 'children'),
    Output('description-text', 'children'),
    Output('description-container', 'style'),
    Output('back-to-news-list', 'n_clicks'),

    Input('back-to-news-list', 'n_clicks'),
    Input({"type": "news-lines", "index": ALL}, 'n_clicks'),

    State('news-table', 'children'),
    prevent_initial_call=True,
)
def toggle_news_display_type(n, cell_clicked, table):
    """
    Function to toggle the display of the news table and the news article
    If a cell is clicked, display the article clicked and hide the table
    Args:
        n: The back button
        cell_clicked: The cell clicked
        table: The news table
    Returns:
        style of the news table
        title of the article
        content of the article
        style of the news article
        n_clicks of the back button (to reset the state)
    """

    # If the back button is clicked, go back to the news list
    if ctx.triggered_id == 'back-to-news-list':
        return {'display': 'block'}, None, None, {'display': 'none'}, [0] * len(cell_clicked)

    else:
        if cell_clicked == [] or 1 not in cell_clicked:
            return no_update, no_update, no_update, no_update, no_update

        try:
            index_clicked = cell_clicked.index(1)  # Get the index of the cell clicked
            rows = table['props']['children'][1]['props']['children']  # get all the rows in the table
            titles = [row['props']['children'][0]['props']['children'] for row in rows]  # get all the titles in the table

            news_df = get_news_dataframe()
            article_clicked = news_df.loc[news_df['title'] == titles[index_clicked]]  # get the news clicked
            return {'display': 'none'}, article_clicked['title'], article_clicked['content'], {'display': 'block'}, no_update
        except Exception as e:
            print(e)
            return no_update, no_update, no_update, no_update, no_update
        

@callback(
    Output('url', 'pathname'),
    State('api-key', 'data'),
    State('alpha', 'data'),
    State('alpha-day-interval', 'data'),
    State('delta', 'data'),
    State('generation-mode', 'data'),
    State('nbr-news', 'data'),
    Input('start-button', 'n_clicks'),
    prevent_initial_call=True
)
def on_start_button_clicked(api_key, alpha, alpha_day_interval, delta, generation_mode, nbr_news, n):
    if n is None:
        raise PreventUpdate

    # TODO : Créer un visuel de chargement
    print("Chargement ...")
    

    #create_news(company, #compny_sector, news_position, 3, 3, 0)
    # TODO : Implémenter les secteurs des entreprises
    # TODO : Créer une section news dans les paramètres pour les paramètres de news

    # Redirect the user to the dashboard
    path = "/dashboard"

    return path