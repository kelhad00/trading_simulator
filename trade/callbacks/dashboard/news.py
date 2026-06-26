from dash import callback, Output, Input, State, page_registry, ALL, no_update, ctx
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dash_iconify import DashIconify
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

    lang = page_registry.get('lang', 'fr')

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
    Output('description-date', 'children'),
    Output('description-text', 'children'),
    Output('description-container', 'style'),
    Output('back-to-news-list', 'n_clicks'),

    Input('back-to-news-list', 'n_clicks'),
    Input({"type": "news-lines", "index": ALL}, 'n_clicks'),

    State('news-table', 'children'),
    prevent_initial_call=True,
)
def toggle_news_display_type(n, cell_clicked, table):
    lang = page_registry.get('lang', 'fr')
    published_label = tls[lang].get('news-published', 'Published:')

    if ctx.triggered_id == 'back-to-news-list':
        return {'display': 'block'}, None, None, None, {'display': 'none'}, [0] * len(cell_clicked)

    if cell_clicked == [] or 1 not in cell_clicked:
        return no_update, no_update, no_update, no_update, no_update, no_update

    try:
        index_clicked = cell_clicked.index(1)
        rows = table['props']['children'][1]['props']['children']
        titles = [row['props']['children'][0]['props']['children'] for row in rows]

        # get_news_dataframe() is cached — negligible cost
        news_df = get_news_dataframe()
        article_clicked = news_df.loc[news_df['title'] == titles[index_clicked]]
        if article_clicked.empty:
            return no_update, no_update, no_update, no_update, no_update, no_update
        title   = article_clicked['title'].iloc[0]
        content = article_clicked['content'].iloc[0]
        date    = str(article_clicked['date'].iloc[0])[:16]
        return {'display': 'none'}, title, f"{published_label} {date}", content, {'display': 'block'}, no_update
    except Exception as e:
        print('Error :', e)
        return no_update, no_update, no_update, no_update, no_update, no_update


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Output('last-notified-ts', 'data'),
    Input('timestamp', 'data'),
    State('last-notified-ts', 'data'),
    State('companies', 'data'),
    prevent_initial_call=True,
)
def notify_new_news(timestamp, last_ts, companies):
    if timestamp is None:
        raise PreventUpdate

    try:
        news_df = get_news_dataframe()
        current_ts = pd.to_datetime(timestamp).replace(tzinfo=None) + pd.Timedelta(days=1)
        current_ts_str = str(current_ts)

        # First tick — just record the timestamp, don't flood with past articles
        if last_ts is None:
            return no_update, current_ts_str

        last_ts_dt = pd.to_datetime(last_ts)

        # Normalise title column
        if 'title' in news_df.columns and 'article' not in news_df.columns:
            news_df = news_df.rename(columns={'title': 'article'})

        new_articles = news_df[
            (news_df['date'] > last_ts_dt) &
            (news_df['date'] <= current_ts)
        ]

        if new_articles.empty:
            return no_update, current_ts_str

        lang = page_registry.get('lang', 'en')
        view_label = tls[lang].get('news-notif-view', 'View')

        notifications = []
        for i, (_, row) in enumerate(new_articles.iterrows()):
            ticker    = str(row.get('ticker', ''))
            sentiment = str(row.get('sentiment', '')).lower()
            headline  = str(row.get('article', row.get('title', '')))

            # Resolve company label and key from the companies store
            company_label = ticker
            company_key   = None
            if companies:
                if ticker in companies:
                    company_key   = ticker
                    company_label = companies[ticker].get('label', ticker)
                else:
                    for key, val in companies.items():
                        if val.get('label', '').lower() == ticker.lower():
                            company_key   = key
                            company_label = val.get('label', ticker)
                            break

            color = "green" if "positive" in sentiment else "red" if "negative" in sentiment else "blue"
            short_headline = headline[:110] + "…" if len(headline) > 110 else headline

            if company_key:
                msg = dmc.Stack([
                    dmc.Text(short_headline, size="xs"),
                    dmc.Button(
                        view_label,
                        id={"type": "news-view-btn", "index": company_key},
                        size="xs",
                        compact=True,
                        variant="outline",
                        color=color,
                        style={"marginTop": "4px"},
                    ),
                ], spacing=2)
            else:
                msg = short_headline

            notifications.append(
                dmc.Notification(
                    id=f"news-notif-{i}-{current_ts_str}",
                    title=company_label,
                    message=msg,
                    color=color,
                    action="show",
                    autoClose=False,
                    icon=DashIconify(icon="material-symbols:newspaper", width=20),
                )
            )

        return notifications, current_ts_str

    except Exception as e:
        print(f"[NEWS NOTIF] Error: {e}")
        raise PreventUpdate


@callback(
    Output('company-selector', 'value', allow_duplicate=True),
    Input({"type": "news-view-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def view_company_from_news_notif(clicks):
    if not any(clicks):
        raise PreventUpdate
    return ctx.triggered_id['index']
