from dash import callback, clientside_callback, Output, Input, State, page_registry, ALL, no_update, ctx, html
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd

_SENTIMENT_COLORS = {"positive": "green", "negative": "red", "neutral": "gray"}

_FONT_SIZES = {'S': '0.75rem', 'M': '0.9375rem', 'L': '1.125rem'}

clientside_callback(
    """function(size) {
        var fs = {'S': '0.75rem', 'M': '0.9375rem', 'L': '1.125rem'}[size] || '0.75rem';
        return [{'fontSize': fs}, {'fontSize': fs}];
    }""",
    Output('news-table', 'style'),
    Output('description-text', 'style'),
    Input('news-font-control', 'value'),
    prevent_initial_call=False,
)

from trade.locales import translations as tls
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
    has_sentiment = 'sentiment' in nl.columns
    nl = nl.head(range)

    date_label = tls[lang]['news-table']['date']
    article_label = tls[lang]['news-table']['article']

    header = html.Thead(html.Tr([
        html.Th(article_label),
        html.Th(date_label, style={"whiteSpace": "nowrap"}),
    ]))

    rows = []
    for idx, row in enumerate(nl.itertuples(index=False)):
        article_text = str(getattr(row, 'article', ''))
        date_text = str(row.date)[:10]

        text_color = None
        if has_sentiment:
            raw = getattr(row, 'sentiment', None)
            sentiment = str(raw).lower().strip() if raw and str(raw) != 'nan' else 'neutral'
            color = _SENTIMENT_COLORS.get(sentiment, "gray")
            if sentiment in ("positive", "negative"):
                text_color = color

        cells = [
            html.Td(article_text, style={"color": text_color} if text_color else {}),
            html.Td(date_text, style={"whiteSpace": "nowrap", "color": "gray", "fontSize": "0.75rem"}),
        ]

        rows.append(html.Tr(
            children=cells,
            id={"type": "news-lines", "index": idx},
            n_clicks=0,
            style={"cursor": "pointer"},
        ))

    return dmc.Table(children=[header, html.Tbody(rows)])


@callback(
    Output('news-container', 'style', allow_duplicate=True),
    Output('description-title', 'children', allow_duplicate=True),
    Output('description-date', 'children', allow_duplicate=True),
    Output('description-text', 'children', allow_duplicate=True),
    Output('description-container', 'style', allow_duplicate=True),
    Output('back-to-news-list', 'n_clicks'),
        Output('description-ticker', 'data', allow_duplicate=True),

    Input('back-to-news-list', 'n_clicks'),
    Input({"type": "news-lines", "index": ALL}, 'n_clicks'),

    State('news-table', 'children'),
    State('companies', 'data'),
    prevent_initial_call=True,
)
def toggle_news_display_type(n, cell_clicked, table, companies):
    lang = page_registry.get('lang', 'fr')
    published_label = tls[lang].get('news-published', 'Published:')

    if ctx.triggered_id == 'back-to-news-list':
        return {'display': 'block'}, None, None, None, {'display': 'none'}, [0] * len(cell_clicked), no_update

    if cell_clicked == [] or 1 not in cell_clicked:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

    try:
        index_clicked = cell_clicked.index(1)
        rows = table['props']['children'][1]['props']['children']
        titles = [row['props']['children'][0]['props']['children'] for row in rows]

        # get_news_dataframe() is cached — negligible cost
        news_df = get_news_dataframe()
        article_clicked = news_df.loc[news_df['title'] == titles[index_clicked]]
        if article_clicked.empty:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update
        title   = article_clicked['title'].iloc[0]
        content = article_clicked['content'].iloc[0]
        date    = str(article_clicked['date'].iloc[0])[:16]

        # Resolve company key from ticker so the View button can navigate to the chart
        company_key = None
        ticker = str(article_clicked['ticker'].iloc[0]) if 'ticker' in article_clicked.columns else ''
        if ticker and companies:
            if ticker in companies:
                company_key = ticker
            else:
                for key, val in companies.items():
                    if val.get('label', '').lower() == ticker.lower():
                        company_key = key
                        break

        return {'display': 'none'}, title, f"{published_label} {date}", content, {'display': 'block'}, no_update, company_key
    except Exception as e:
        print('Error :', e)
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update


@callback(
    Output('company-selector', 'value', allow_duplicate=True),
    Input('description-view-btn', 'n_clicks'),
    State('description-ticker', 'data'),
    prevent_initial_call=True,
)
def view_company_from_description(n_clicks, company_key):
    if not n_clicks or not company_key:
        raise PreventUpdate
    return company_key


@callback(
    Output('notifications', 'children', allow_duplicate=True),
    Output('last-notified-ts', 'data'),
    Input('periodic-updater', 'n_intervals'),
    State('timestamp', 'data'),
    State('last-notified-ts', 'data'),
    State('companies', 'data'),
    State('notif-filter', 'data'),
    State('notif-offset', 'data'),
    prevent_initial_call=True,
)
def notify_new_news(n, timestamp, last_ts, companies, notif_filter, notif_offset):
    if timestamp is None:
        raise PreventUpdate

    try:
        news_df = get_news_dataframe()
        current_ts = pd.to_datetime(timestamp).replace(tzinfo=None) + pd.Timedelta(days=1)
        offset_days = int(notif_offset or 0)
        notify_ts = current_ts + pd.Timedelta(days=offset_days)
        notify_ts_str = str(notify_ts)

        # First tick — just record the position, don't flood with past articles
        if last_ts is None:
            return no_update, notify_ts_str

        last_ts_dt = pd.to_datetime(last_ts)

        # If last_ts is ahead of the current notify window (stale from a previous run),
        # treat it as None so notifications restart from the beginning
        if last_ts_dt > notify_ts:
            return no_update, notify_ts_str

        new_articles = news_df[
            (news_df['date'] > last_ts_dt) &
            (news_df['date'] <= notify_ts)
        ]

        # Apply sentiment filter
        allowed = set(notif_filter) if notif_filter else set()
        if allowed and 'sentiment' in new_articles.columns:
            new_articles = new_articles[
                new_articles['sentiment'].str.lower().str.strip().isin(allowed)
            ]

        if new_articles.empty:
            return no_update, notify_ts_str

        lang = page_registry.get('lang', 'en')
        view_label = tls[lang].get('news-notif-view', 'View')

        notifications = []
        for i, (_, row) in enumerate(new_articles.iterrows()):
            ticker    = str(row.get('ticker', ''))
            sentiment = str(row.get('sentiment', '')).lower()
            title_col = 'article' if 'article' in row.index else 'title'
            headline  = str(row.get(title_col, ''))

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

            text_color = color if color in ("green", "red") else None
            styled_headline = (
                html.Span(short_headline, style={"color": text_color})
                if text_color else short_headline
            )

            safe_ts = notify_ts_str.replace(":", "-").replace(" ", "-")
            if company_key:
                msg = dmc.Stack([
                    dmc.Text(styled_headline, size="xs"),
                    dmc.Button(
                        view_label,
                        id={"type": "news-view-btn", "index": headline},
                        size="xs",
                        variant="outline",
                        color=color,
                        style={"marginTop": "4px"},
                    ),
                ], spacing="xs")
            else:
                msg = styled_headline

            notifications.append(
                dmc.Notification(
                    id=f"news-notif-{i}-{safe_ts}",
                    title=company_label,
                    message=msg,
                    color=color,
                    action="show",
                    autoClose=5000,
                    icon=DashIconify(icon="material-symbols:newspaper", width=20),
                )
            )

        return notifications, notify_ts_str

    except Exception as e:
        print(f"[NEWS NOTIF] Error: {e}")
        raise PreventUpdate


@callback(
    Output('news-container', 'style', allow_duplicate=True),
    Output('description-title', 'children', allow_duplicate=True),
    Output('description-date', 'children', allow_duplicate=True),
    Output('description-text', 'children', allow_duplicate=True),
    Output('description-container', 'style', allow_duplicate=True),
    Output('description-ticker', 'data', allow_duplicate=True),
    Input({"type": "news-view-btn", "index": ALL}, "n_clicks"),
    State('companies', 'data'),
    prevent_initial_call=True,
)
def view_article_from_news_notif(clicks, companies):
    if not any(clicks):
        raise PreventUpdate
    article_title = ctx.triggered_id['index']
    try:
        news_df = get_news_dataframe()
        lang = page_registry.get('lang', 'fr')
        published_label = tls[lang].get('news-published', 'Published:')
        article = news_df.loc[news_df['title'] == article_title]
        if article.empty:
            raise PreventUpdate
        title   = article['title'].iloc[0]
        content = article['content'].iloc[0]
        date    = str(article['date'].iloc[0])[:16]
        ticker  = str(article['ticker'].iloc[0]) if 'ticker' in article.columns else ''
        company_key = None
        if ticker and companies:
            if ticker in companies:
                company_key = ticker
            else:
                for key, val in companies.items():
                    if val.get('label', '').lower() == ticker.lower():
                        company_key = key
                        break
        return {'display': 'none'}, title, f"{published_label} {date}", content, {'display': 'block'}, company_key
    except PreventUpdate:
        raise
    except Exception as e:
        print(f"[NOTIF VIEW] Error: {e}")
        raise PreventUpdate
