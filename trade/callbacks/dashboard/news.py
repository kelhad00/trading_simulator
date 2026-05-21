from dash import callback, Output, Input, State, page_registry, ALL, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
import pandas as pd

from trade.locales import translations as tls
from trade.components.table import create_table
from trade.utils.news import get_news_dataframe


@callback(
    Output('news-table', 'children'),
    Input('periodic-updater', 'n_intervals'),
    State('timestamp', 'data'),
)
def cb_update_news_table(n, timestamp, range=50, daily=True):
    try:
        # get_news_dataframe() is cached — only re-reads CSV when the file changes
        news_df = get_news_dataframe()
    except Exception as e:
        print(f"[NEWS] Could not load news.csv: {e}")
        raise PreventUpdate

    lang = page_registry['lang']

    # Normalise column name: support both 'title' and 'article'
    if 'title' in news_df.columns:
        news_df = news_df.rename(columns={'title': 'article'})
    elif 'article' not in news_df.columns:
        print("[NEWS] news.csv has no 'title' or 'article' column — columns found:", news_df.columns.tolist())
        raise PreventUpdate

    news_df = news_df.drop_duplicates(subset=['article'], keep='first')

    # Dates are already parsed by get_news_dataframe() — no need to re-parse
    try:
        ts = pd.to_datetime(timestamp).replace(tzinfo=None)
        if daily:
            ts = ts + pd.Timedelta(days=1)
    except Exception as e:
        print(f"[NEWS] Timestamp conversion failed (value={timestamp}): {e}")
        ts = pd.Timestamp.now()

    nl = news_df.loc[news_df['date'] <= ts].sort_values(by='date', ascending=False)
    nl = nl[['article', 'date']].head(range).astype(str)
    nl = nl.rename(columns={
        'date': tls[lang]['news-table']['date'],
        'article': tls[lang]['news-table']['article'],
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
    if ctx.triggered_id == 'back-to-news-list':
        return {'display': 'block'}, None, None, {'display': 'none'}, [0] * len(cell_clicked)

    if cell_clicked == [] or 1 not in cell_clicked:
        return no_update, no_update, no_update, no_update, no_update

    try:
        index_clicked = cell_clicked.index(1)
        rows = table['props']['children'][1]['props']['children']
        titles = [row['props']['children'][0]['props']['children'] for row in rows]

        # get_news_dataframe() is cached — negligible cost
        news_df = get_news_dataframe()
        article_clicked = news_df.loc[news_df['title'] == titles[index_clicked]]
        return {'display': 'none'}, article_clicked['title'], article_clicked['content'], {'display': 'block'}, no_update
    except Exception as e:
        print('Error :', e)
        return no_update, no_update, no_update, no_update, no_update
