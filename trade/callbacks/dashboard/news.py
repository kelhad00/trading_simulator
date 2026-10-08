from dash import callback, clientside_callback, Output, Input, State, ALL, no_update, ctx, html
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd

# The 5 news tags and their colour. The tag (FinBERT's reading of the article,
# column `sentiment_label`) decides both the badge and the headline colour.
_TAG_COLORS = {
    "strong positive": "green",
    "weak positive":   "teal",
    "neutral":         "gray",
    "weak negative":   "orange",
    "strong negative": "red",
}


def _news_tag(raw_label):
    """One of the 5 tags; "no positive", "no negative", empty or unknown become neutral."""
    label = str(raw_label).lower().strip() if raw_label is not None else ""
    return label if label in _TAG_COLORS else "neutral"


def _tag_direction(tag):
    """positive / negative / neutral, as used by the notification filter."""
    return tag.split()[-1] if tag != "neutral" else "neutral"

_FONT_SIZES = {'S': '0.75rem', 'M': '0.9375rem', 'L': '1.125rem'}


def _headline_text(children):
    """Headline text of a news-table article cell.

    Rows with a sentiment tag hold [badge, text] instead of just the text, so
    the badge must be skipped to find the article by its title.
    """
    if isinstance(children, list):
        return next((c for c in children if isinstance(c, str)), None)
    return children

clientside_callback(
    """function(size) {
        var fs = {'S': '0.75rem', 'M': '0.9375rem', 'L': '1.125rem'}[size] || '0.75rem';
        return [{'fontSize': fs}, {'fontSize': fs}];
    }""",
    Output('news-table', 'style'),
    Output('description-text', 'style'),
    Input('news-font-size', 'data'),
    prevent_initial_call=False,
)

from trade.locales import translations as tls, language
from trade.utils.news import get_news_dataframe
from trade.utils.market import get_market_dataframe
from trade.utils.news_timing import article_positions, now_position, visible
from trade.utils.logs import get_logger

logger = get_logger("news")


@callback(
    Output('news-table', 'children'),
    Output('news-table-key', 'data'),
    State('timestamp', 'data'),
    State('candle-step', 'data'),
    State('news-table-key', 'data'),
    State('steps-per-candle', 'data'),
    # Woken only when a new article appears (see update_graph), not on every tick
    Input('news-clock', 'data'),
    State("url", "search"),     # ?lang=en in this participant's address
)
def cb_update_news_table(timestamp, candle_step=None, shown_key=None, steps_per_candle=1, news_clock=None, lang=None, range=50):
    try:
        # get_news_dataframe() is cached — only re-reads CSV when the file changes
        news_df = get_news_dataframe()
    except Exception as e:
        logger.warning("Could not load news.csv: %s", e)
        raise PreventUpdate

    lang = language(lang)

    # Normalise column name: support both 'title' and 'article'
    if 'title' in news_df.columns:
        news_df = news_df.rename(columns={'title': 'article'})
    elif 'article' not in news_df.columns:
        logger.warning("news.csv has no 'title' or 'article' column, columns found: %s", news_df.columns.tolist())
        raise PreventUpdate

    news_df = news_df.drop_duplicates(subset=['article'], keep='first')

    # Only articles that have appeared: their own candle, at their step (never a day early)
    try:
        market_index = get_market_dataframe().index
        positions = article_positions(news_df, market_index, steps_per_candle, title_column='article')
        now = now_position(market_index, timestamp, candle_step, steps_per_candle)
    except Exception as e:
        logger.warning("Could not work out which news has appeared (timestamp=%s): %s", timestamp, e)
        raise PreventUpdate

    nl = news_df.loc[visible(positions, now)].sort_values(by='date', ascending=False)
    has_label = 'sentiment_label' in nl.columns
    nl = nl.head(range)

    # Only send the list when it changed (new news, or another language): it is
    # checked every tick, but most ticks bring no new news.
    key = [lang] + [[str(d), str(a)] for d, a in zip(nl['date'], nl['article'])]
    if key == shown_key:
        return no_update, no_update

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

        # Every headline gets one of the 5 tags; badge and text share its colour
        tag = _news_tag(getattr(row, 'sentiment_label', None) if has_label else None)
        color = _TAG_COLORS[tag]
        badge = dmc.Badge(tag, color=color, size="xs", variant="light",
                          style={"marginRight": "6px", "verticalAlign": "middle"})

        cells = [
            html.Td([badge, article_text], style={"color": color}),
            html.Td(date_text, style={"whiteSpace": "nowrap", "color": "gray", "fontSize": "0.75rem"}),
        ]

        rows.append(html.Tr(
            children=cells,
            id={"type": "news-lines", "index": idx},
            n_clicks=0,
            style={"cursor": "pointer"},
        ))

    return dmc.Table(children=[header, html.Tbody(rows)]), key


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
    State("url", "search"),     # ?lang=en in this participant's address
    prevent_initial_call=True,
)
def toggle_news_display_type(n, cell_clicked, table, companies, lang=None):
    lang = language(lang)
    published_label = tls[lang].get('news-published', 'Published:')

    if ctx.triggered_id == 'back-to-news-list':
        return {'display': 'block'}, None, None, None, {'display': 'none'}, [0] * len(cell_clicked), no_update

    # The headline that was just clicked. The list is no longer rebuilt every tick,
    # so its click counters aren't reset: clicking the same headline again (2, 3…)
    # must open it too. A rebuilt list (all counters at 0) opens nothing.
    trigger = ctx.triggered_id
    if not isinstance(trigger, dict) or trigger.get("index") is None:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update
    index_clicked = trigger["index"]
    if index_clicked >= len(cell_clicked) or not cell_clicked[index_clicked]:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

    try:
        rows = table['props']['children'][1]['props']['children']
        titles = [_headline_text(row['props']['children'][0]['props']['children']) for row in rows]

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
        logger.error("Could not open the news article: %s", e)
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
    State('timestamp', 'data'),
    State('candle-step', 'data'),
    State('last-notified-ts', 'data'),
    State('companies', 'data'),
    State('notif-filter', 'data'),
    State('notif-offset', 'data'),
    State('notif-enabled', 'data'),
    State('steps-per-candle', 'data'),
    # Woken only when a new article appears (see update_graph), not on every tick.
    # Also when the page opens, to note where the session is: articles after that pop up.
    Input('news-clock', 'data'),
    State("url", "search"),     # ?lang=en in this participant's address
    prevent_initial_call='initial_duplicate',
)
def notify_new_news(timestamp, candle_step, last_seen, companies, notif_filter, notif_offset, notif_enabled,
                    steps_per_candle=1, news_clock=None, lang=None):
    if timestamp is None:
        raise PreventUpdate

    if not notif_enabled:
        return no_update, no_update

    try:
        news_df = get_news_dataframe()
        market_index = get_market_dataframe().index
        # 'Warn me X days early' setting: look that many candles ahead
        now = now_position(market_index, timestamp, candle_step, steps_per_candle,
                           candles_ahead=int(notif_offset or 0))
        notify_ts_str = f"{now[0]}-{now[1]}"

        # First time — just record the position, don't flood with past articles.
        # (An older version stored a date string here: treated the same way.)
        if not isinstance(last_seen, list) or len(last_seen) != 2:
            return no_update, list(now)
        last_seen = tuple(last_seen)

        # The session went back (reset / new session): restart from here
        if last_seen > now:
            return no_update, list(now)

        positions = article_positions(news_df, market_index, steps_per_candle)
        new_articles = news_df[positions.map(lambda p: last_seen < tuple(p) <= now)]

        # Apply sentiment filter (positive / negative / neutral), by the article's tag
        allowed = set(notif_filter) if notif_filter else set()
        if allowed:
            labels = new_articles['sentiment_label'] if 'sentiment_label' in new_articles.columns \
                else pd.Series(None, index=new_articles.index)
            directions = labels.map(lambda raw: _tag_direction(_news_tag(raw)))
            new_articles = new_articles[directions.isin(allowed)]

        if new_articles.empty:
            return no_update, list(now)

        lang = language(lang)
        view_label = tls[lang].get('news-notif-view', 'View')

        notifications = []
        for i, (_, row) in enumerate(new_articles.iterrows()):
            ticker    = str(row.get('ticker', ''))
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

            # Same tag and colour as in the news list
            color = _TAG_COLORS[_news_tag(row.get('sentiment_label'))]
            short_headline = headline[:110] + "…" if len(headline) > 110 else headline
            styled_headline = html.Span(short_headline, style={"color": color})

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

        return notifications, list(now)

    except Exception as e:
        logger.error("News notification error: %s", e)
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
    State("url", "search"),     # ?lang=en in this participant's address
    prevent_initial_call=True,
)
def view_article_from_news_notif(clicks, companies, lang=None):
    if not any(clicks):
        raise PreventUpdate
    article_title = ctx.triggered_id['index']
    try:
        news_df = get_news_dataframe()
        lang = language(lang)
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
        logger.error("Notification 'view' button error: %s", e)
        raise PreventUpdate
