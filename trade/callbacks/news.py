from dash import html, dcc, callback, Output, Input, State, page_registry, ALL, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

import os
import pandas as pd

from trade.defaults import defaults as dlt
from trade.Locales import translations as tls
from trade.utils.create_table import create_table
from trade.utils.news import get_news_dataframe


@callback(
    Output('news-table', 'children'),
    Input('periodic-updater', 'n_intervals'),
    State('timestamp', 'data'),
)
def cb_update_news_table(n, timestamp, range=50, daily=True):
    news_df = get_news_dataframe()

    try:
        news_df = news_df.drop_duplicates(subset=['title'], keep='first') \
            .rename({'title': 'article'}, axis=1)
    except KeyError:  # Else, if news_df contains an article column
        try:
            news_df = news_df.drop_duplicates(subset=['article'], keep='first')
        except KeyError:  # news _df is not correctly formatted
            print('WARNING: The `news.csv` file must contain a `title` or `article` column.')
            raise PreventUpdate

    news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True, format='mixed')

    # Convert timestamp to datetime to the format used by the news dataframe
    timestamp = pd.to_datetime(timestamp).tz_localize(None)

    if daily:
        timestamp = timestamp + pd.Timedelta(days=1)

    # Get the news before the timestamp
    nl = news_df.loc[news_df['date'] <= timestamp].sort_values(by='date', ascending=False).astype(str)

    lang = page_registry['lang']
    #Display only article and date columns
    nl = nl[['article', 'date']]
    nl = nl.rename(columns={'date': tls[lang]['news-table']['date'], 'article': tls[lang]['news-table']['article']})

    return dmc.Table(
        children=create_table(nl[:range], id="news-lines"),
    )



@callback(
    Output('news-container', 'style'),
    Output('description-title', 'children'),
    Output('description-text', 'children'),
    Output('description-container', 'style'),
    Output('back-to-news-list', 'n_clicks'),
    Input({"type": "news-lines", "index": ALL}, 'n_clicks'),
    Input('back-to-news-list', 'n_clicks'),
    State('news-table', 'children'),

)
def show_hide_element(cell_clicked, n_back_button, table):
    """Hide News table & Show News description when News table cell clicked"""

    if ctx.triggered_id == 'back-to-news-list':
        print('back button clicked')
        return {'display': 'block'}, '', '', {'display': 'none'}, [0] * len(cell_clicked)

    else:
        if cell_clicked == [] or 1 not in cell_clicked:
            return no_update, no_update, no_update, no_update, no_update

        try:
            index_clicked = cell_clicked.index(1)
            rows = table['props']['children'][1]['props']['children']
            titles = [row['props']['children'][0]['props']['children'] for row in rows]
            news_df = get_news_dataframe()
            article_clicked = news_df.loc[news_df['title'] == titles[index_clicked]]
            print(article_clicked)
            return {'display': 'none'}, article_clicked['title'], article_clicked['content'], {'display': 'block'}, no_update
        except Exception as e:
            print(e)
            return no_update, no_update, no_update, no_update, no_update

