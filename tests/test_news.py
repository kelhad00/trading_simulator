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
    built, _key = news.cb_update_news_table(1, "2025-01-20 00:00:00")
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


def click(monkeypatch, table, index, clicks):
    """Click headline `index`; `clicks` = click counters of all headlines, as the browser sends them."""
    monkeypatch.setattr(news, "ctx", SimpleNamespace(triggered_id={"type": "news-lines", "index": index}))
    return news.toggle_news_display_type(0, clicks, table, {})[1]


def test_every_headline_opens_its_article(table, monkeypatch):
    n = len(rows(table))
    for i in range(n):
        clicks = [0] * n
        clicks[i] = 1
        assert click(monkeypatch, table, i, clicks) is not news.no_update, f"headline {i} did not open"


def test_same_headline_opens_again_after_going_back(table, monkeypatch):
    """The list is no longer rebuilt every tick, so a second click counts 2."""
    n = len(rows(table))
    clicks = [0] * n
    clicks[2] = 2
    assert click(monkeypatch, table, 2, clicks) is not news.no_update


def test_a_freshly_drawn_list_opens_nothing(table, monkeypatch):
    n = len(rows(table))
    assert click(monkeypatch, table, 0, [0] * n) is news.no_update


def test_headline_text_ignores_the_tag():
    assert news._headline_text("Plain title") == "Plain title"
    assert news._headline_text([{"type": "Badge"}, "Tagged title"]) == "Tagged title"
