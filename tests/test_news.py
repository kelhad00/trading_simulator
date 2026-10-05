"""News list: exactly 5 tags, the tag decides the colour, and every headline opens."""
import json
from types import SimpleNamespace

import plotly
import pytest

import trade.callbacks.dashboard.news as news

FIVE_TAGS = {"strong positive", "weak positive", "neutral", "weak negative", "strong negative"}


@pytest.mark.parametrize("raw, expected", [
    ("strong positive", "strong positive"),
    ("  Weak Negative ", "weak negative"),
    ("no positive", "neutral"),
    ("no negative", "neutral"),
    ("", "neutral"),
    (None, "neutral"),
    (float("nan"), "neutral"),
    ("something else", "neutral"),
])
def test_only_five_tags_exist(raw, expected):
    assert news._news_tag(raw) == expected


def test_tag_direction_for_the_notification_filter():
    assert news._tag_direction("strong positive") == "positive"
    assert news._tag_direction("weak negative") == "negative"
    assert news._tag_direction("neutral") == "neutral"


@pytest.fixture
def table(fake_data):
    """The news table as the browser receives it."""
    built = news.cb_update_news_table(1, "2025-01-20 00:00:00")
    return json.loads(json.dumps(built, cls=plotly.utils.PlotlyJSONEncoder))


def rows(table):
    return table["props"]["children"][1]["props"]["children"]


def test_every_headline_has_one_of_the_five_tags_in_the_same_colour(table):
    assert len(rows(table)) == 5
    for row in rows(table):
        cell = row["props"]["children"][0]["props"]
        badge = cell["children"][0]["props"]
        assert badge["children"] in FIVE_TAGS
        assert badge["color"] == cell["style"]["color"]


def test_contradicting_article_is_shown_with_its_tag_colour(table):
    """Written as positive but read as strong negative: shown red, not green with a red tag."""
    cell = next(r["props"]["children"][0]["props"] for r in rows(table)
                if "efficiency drive" in r["props"]["children"][0]["props"]["children"][1])
    assert cell["style"]["color"] == "red"


def test_every_headline_opens_its_article(table, monkeypatch):
    monkeypatch.setattr(news, "ctx", SimpleNamespace(triggered_id={"type": "news-lines", "index": 0}))
    n = len(rows(table))
    for i in range(n):
        clicks = [0] * n
        clicks[i] = 1
        title = news.toggle_news_display_type(0, clicks, table, {})[1]
        assert title is not news.no_update, f"headline {i} did not open"


def test_headline_text_ignores_the_tag():
    assert news._headline_text("Plain title") == "Plain title"
    assert news._headline_text([{"type": "Badge"}, "Tagged title"]) == "Tagged title"
