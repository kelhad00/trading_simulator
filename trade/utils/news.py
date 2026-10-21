import os
import pandas as pd

from trade.defaults import defaults as dlt
from trade.utils.logs import get_logger

logger = get_logger("news-data")

# mtime-based cache — [dataframe, mtime]
_news_cache: list = [None, -1.0]


def get_news_dataframe():
    file_path = os.path.join(dlt.data_path, 'news.csv')
    try:
        mtime = os.path.getmtime(file_path)
        if _news_cache[0] is not None and _news_cache[1] == mtime:
            return _news_cache[0]

        news_df = pd.read_csv(file_path, sep=';')
        # Strip timezone suffix (+02:00 / +01:00) so both date formats parse cleanly
        news_df['date'] = news_df['date'].astype(str).str.replace(
            r'\s*[+-]\d{2}:\d{2}$', '', regex=True
        )
        news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True, format='mixed')

        _news_cache[0] = news_df
        _news_cache[1] = mtime
        return news_df
    except Exception as e:
        logger.warning("Could not read news.csv: %s", e)
        raise FileNotFoundError


# Articles are stored in both languages (columns title_fr, content_fr, title_en,
# content_en, see news_generation/news_creation.py). 'title'/'content' hold the
# original version: the article's identity (news timing, logs) and the fallback.

def _filled(value):
    return value is not None and not pd.isna(value) and str(value).strip() != ""


def article_text(row, lang):
    """(title, content) of an article in the participant's language, or the original
    when that translation is missing (old news files, failed translation).
    `row`: a dict or a pandas row; its title may be named 'title' or 'article'."""
    get = row.get if hasattr(row, "get") else (lambda key, default=None: getattr(row, key, default))
    title, content = get(f"title_{lang}"), get(f"content_{lang}")
    if _filled(title) and _filled(content):
        return str(title), str(content)
    original = get("title")
    if not _filled(original):
        original = get("article", "")
    return str(original), str(get("content", "") or "")


def find_article(news_df, shown_title):
    """The article(s) whose title, in any language, is the headline shown on screen."""
    columns = [c for c in news_df.columns if c in ("title", "article") or c.startswith("title_")]
    match = pd.Series(False, index=news_df.index)
    for column in columns:
        match |= news_df[column].astype(str) == str(shown_title)
    return news_df[match]
