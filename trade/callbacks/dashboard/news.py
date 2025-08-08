from dash import callback, Output, Input, State, page_registry, ALL, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import pandas as pd

from trade.locales import translations as tls
from trade.components.table import create_table
from trade.utils.news import get_news_dataframe
from trade.defaults import defaults as dlt


def get_next_timestamp_by_granularity(current_timestamp, granularity):
    """
    Get the next timestamp based on the granularity setting
    
    Args:
        current_timestamp: The current timestamp
        granularity: The granularity setting ('H', 'D', 'W', 'M')
    
    Returns:
        The next timestamp based on granularity
    """
    if not current_timestamp:
        return current_timestamp
    
    # Ensure timestamp is properly parsed and convert to timezone-naive
    try:
        timestamp = pd.to_datetime(current_timestamp).tz_localize(None)
    except:
        # If parsing fails, try without timezone
        timestamp = pd.to_datetime(current_timestamp)
    
    if granularity == 'H':
        # Next hour
        return timestamp + pd.Timedelta(hours=1)
    elif granularity == 'D':
        # Next day
        return timestamp + pd.Timedelta(days=1)
    elif granularity == 'W':
        # Next week
        return timestamp + pd.Timedelta(weeks=1)
    elif granularity == 'M':
        # Next month
        return timestamp + pd.DateOffset(months=1)
    else:
        # Default to next day
        return timestamp + pd.Timedelta(days=1)


@callback(
    Output('news-table', 'children'),
    Input('periodic-updater', 'n_intervals'),
    Input('selected-interval', 'data'),
    State('timestamp', 'data'),
)
def cb_update_news_table(n, selected_interval, timestamp, range=50):
    """
    Function to display the latest news in the table from the timestamp
    Args:
        timestamp: The last timestamp
    Returns:
        The updated news table
    """
    lang = page_registry['lang']

    try:
        news_df = get_news_dataframe(lang)
    except FileNotFoundError:
        raise "The news_fr.csv file was not generated."


    # Format the news dataframe
    try:
        news_df = news_df.drop_duplicates(subset=['title'], keep='first') \
            .rename({'title': 'article'}, axis=1)
    except KeyError:  # Else, if news_df contains an article column
        try:
            news_df = news_df.drop_duplicates(subset=['article'], keep='first')
        except KeyError:  # news _df is not correctly formatted
            print('WARNING: The `news_fr.csv` file must contain a `title` or `article` column.')
            raise PreventUpdate

    # Convert the date column and the timestamp to datetime
    news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True, format='mixed')
    timestamp = pd.to_datetime(timestamp).tz_localize(None)

    # Get the next timestamp based on selected time unit instead of adding one day
    current_interval = selected_interval if selected_interval else dlt.granularity
    # Normalize interval keys for this module's helper (expects upper-case for hour/month)
    mapping = { 'h': 'H', 'D': 'D', 'W': 'W', 'ME': 'M' }
    news_interval = mapping.get(current_interval, 'D')
    next_timestamp = get_next_timestamp_by_granularity(timestamp, news_interval)

    # Get the news before the next timestamp
    nl = news_df.loc[news_df['date'] <= next_timestamp].sort_values(by='date', ascending=False).astype(str)

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
    lang = page_registry['lang']

    if ctx.triggered_id == 'back-to-news-list':
        return {'display': 'block'}, None, None, {'display': 'none'}, [0] * len(cell_clicked)

    else:
        if cell_clicked == [] or 1 not in cell_clicked:
            return no_update, no_update, no_update, no_update, no_update

        try:
            index_clicked = cell_clicked.index(1)  # Get the index of the cell clicked
            rows = table['props']['children'][1]['props']['children']  # get all the rows in the table
            titles = [row['props']['children'][0]['props']['children'] for row in rows]  # get all the titles in the table

            news_df = get_news_dataframe(lang=lang)
            article_clicked = news_df.loc[news_df['title'] == titles[index_clicked]]  # get the news clicked
            return {'display': 'none'}, article_clicked['title'], article_clicked['content'], {'display': 'block'}, no_update
        except Exception as e:
            print('Error :', e)
            return no_update, no_update, no_update, no_update, no_update