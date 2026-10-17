"""The news sentiment tags (and their colours) can be switched off in Settings -> News,
so in some experiments participants have to read the news to know if it is good or bad."""
import io
import json
import zipfile
from types import SimpleNamespace

import plotly

import trade.callbacks.dashboard.news as news
import trade.callbacks.settings.news as news_settings
from trade.utils.session import build_session_zip, extract_session_zip

NOW = "2025-01-20 00:00:00"


def article_cells(show_tags):
    built, _key = news.cb_update_news_table(NOW, None, None, 1, None, None, show_tags)
    table = json.loads(json.dumps(built, cls=plotly.utils.PlotlyJSONEncoder))
    return [r["props"]["children"][0]["props"] for r in table["props"]["children"][1]["props"]["children"]]


def test_tags_off_headlines_are_plain_text(fake_data):
    for cell in article_cells(False):
        assert isinstance(cell["children"], str)      # no badge
        assert "style" not in cell                    # no colour


def test_tags_on_or_nothing_saved_shows_tags(fake_data):
    for show_tags in (True, None):
        for cell in article_cells(show_tags):
            assert cell["children"][0]["props"]["children"] in news._TAG_COLORS


def test_switching_tags_rebuilds_the_list(fake_data):
    _, key = news.cb_update_news_table(NOW, None, None, 1, None, None, True)
    table, _ = news.cb_update_news_table(NOW, None, key, 1, None, None, False)
    assert table is not news.no_update


def test_headline_still_opens_with_tags_off(fake_data, monkeypatch):
    built, _ = news.cb_update_news_table(NOW, None, None, 1, None, None, False)
    table = json.loads(json.dumps(built, cls=plotly.utils.PlotlyJSONEncoder))
    monkeypatch.setattr(news, "ctx", SimpleNamespace(triggered_id={"type": "news-lines", "index": 0}))
    clicks = [1] + [0] * (len(article_cells(False)) - 1)
    assert news.toggle_news_display_type(0, clicks, table, {})[1] is not news.no_update


def test_notification_colour():
    assert news._notification_color("strong negative", True) == "red"
    assert news._notification_color("strong negative", None) == "red"         # default: tags on
    assert news._notification_color("strong negative", False) == news._NO_TAG_COLOR
    assert news._notification_color("strong positive", False) == news._NO_TAG_COLOR


def test_switch_shows_and_saves_the_setting():
    assert news_settings.show_news_tags_setting("news", False) is False
    assert news_settings.show_news_tags_setting("news", None) is True         # default: on
    assert news_settings.save_news_tags_setting(False) is False
    assert news_settings.save_news_tags_setting(True) is True


def test_setting_is_kept_in_session_files(fake_data, tmp_path):
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data), news_tags_enabled=False)
    assert extract_session_zip(raw, str(tmp_path))["news-tags-enabled"] is False


def test_old_session_files_keep_tags_on(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("session.json", json.dumps({"version": 1, "stores": {
            "companies": {}, "initial-cashflow": 100_000, "max-requests": 10, "update-time": 5000}}))
    assert extract_session_zip(buf.getvalue(), str(tmp_path))["news-tags-enabled"] is True
