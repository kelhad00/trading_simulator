"""News in both languages: each article is written in the Settings page's language,
then translated; the dashboard shows the participant's language (the original when a
translation is missing). The AI is replaced by a stand-in: no AI credit is used."""
import json
from types import SimpleNamespace

import pandas as pd
import plotly

import trade.callbacks.dashboard.news as news
import trade.utils.news_generation.news_creation as nc
from trade.utils.news import article_text, find_article, get_news_dataframe
from trade.utils.news_timing import article_positions
from trade.utils.market import get_market_dataframe

NOW = "2025-01-20 00:00:00"
EN = "AAA beats expectations"
FR = "AAA dépasse les attentes"


def add_translations(fake_data):
    """The fake news.csv, with French translations for the first article only."""
    path = fake_data / "news.csv"
    df = pd.read_csv(path, sep=";")
    df["title_en"], df["content_en"] = df["title"], df["content"]
    df["title_fr"], df["content_fr"] = "", ""
    df.loc[df["title"] == EN, ["title_fr", "content_fr"]] = [FR, "Un trimestre solide."]
    df.to_csv(path, sep=";", index=False)


# ── Showing the right language ───────────────────────────────────────────

def test_article_in_the_participants_language():
    row = {"title": EN, "content": "Strong quarter.", "title_fr": FR, "content_fr": "Un trimestre solide.",
           "title_en": EN, "content_en": "Strong quarter."}
    assert article_text(row, "fr") == (FR, "Un trimestre solide.")
    assert article_text(row, "en") == (EN, "Strong quarter.")


def test_missing_translation_shows_the_original():
    assert article_text({"title": EN, "content": "x", "title_fr": float("nan"), "content_fr": ""}, "fr") == (EN, "x")
    assert article_text({"title": EN, "content": "x"}, "fr") == (EN, "x")          # old news file


def headlines(lang):
    built, _ = news.cb_update_news_table(NOW, None, None, 1, None, f"?lang={lang}")
    table = json.loads(json.dumps(built, cls=plotly.utils.PlotlyJSONEncoder))
    rows = table["props"]["children"][1]["props"]["children"]
    return table, [news._headline_text(r["props"]["children"][0]["props"]["children"]) for r in rows]


def test_news_list_follows_the_app_language(fake_data):
    add_translations(fake_data)
    _, fr = headlines("fr")
    _, en = headlines("en")
    assert FR in fr and EN not in fr
    assert EN in en and FR not in en
    assert len(fr) == len(en) == 5                     # same articles, same moment


def test_both_languages_appear_at_the_same_moment(fake_data):
    add_translations(fake_data)
    df = get_news_dataframe()
    positions = article_positions(df, get_market_dataframe().index, 4)
    assert len(set(positions)) == len(df)              # timing still uses the original title


def test_a_french_headline_opens_the_french_article(fake_data, monkeypatch):
    add_translations(fake_data)
    table, fr = headlines("fr")
    i = fr.index(FR)
    clicks = [0] * len(fr)
    clicks[i] = 1
    monkeypatch.setattr(news, "ctx", SimpleNamespace(triggered_id={"type": "news-lines", "index": i}))
    out = news.toggle_news_display_type(0, clicks, table, {}, "?lang=fr")
    assert out[1] == FR
    assert out[3] == "Un trimestre solide."


def test_find_article_by_any_language(fake_data):
    add_translations(fake_data)
    df = get_news_dataframe()
    assert len(find_article(df, FR)) == 1
    assert len(find_article(df, EN)) == 1
    assert find_article(df, "not a headline").empty


def test_pop_up_view_button_opens_the_article_in_french(fake_data, monkeypatch):
    add_translations(fake_data)
    monkeypatch.setattr(news, "ctx", SimpleNamespace(triggered_id={"type": "news-view-btn", "index": FR}))
    out = news.view_article_from_news_notif([1], {}, "?lang=fr")
    assert out[1] == FR


# ── Generating: write, then translate ────────────────────────────────────

def fake_ai(*answers):
    """A stand-in AI client that gives these answers in turn."""
    feed = iter(answers)
    create = lambda **kw: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=next(feed)))])
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


def test_translation_is_parsed_and_checked():
    client = fake_ai("TITRE: Hausse record pour AAA\nARTICLE: AAA a annoncé des résultats solides pour le trimestre et les ventes sont en hausse.")
    title, content = nc.translate_article("AAA soars", "AAA reported strong results.", "fr", "AAA", client, "m")
    assert title == "Hausse record pour AAA"
    assert content.startswith("AAA a annoncé")


def test_wrong_language_is_retried_then_left_empty():
    wrong = "TITLE: AAA soars\nARTICLE: AAA reported strong results for the quarter and sales are up."
    client = fake_ai(wrong, wrong, wrong)
    assert nc.translate_article("AAA soars", "x", "fr", "AAA", client, "m") == ("", "")


def test_thinking_notes_before_the_answer_are_skipped():
    text = "<think>TITRE: draft\nARTICLE: draft</think>\nTITRE: AAA en hausse\nARTICLE: Les ventes montent."
    assert nc._parse_translation(text) == ("AAA en hausse", "Les ventes montent.")


def test_badly_formatted_answer_is_retried():
    good = "TITRE: AAA en hausse\nARTICLE: Les ventes de AAA sont en hausse et le marché est confiant pour la suite."
    client = fake_ai("Sure! Here it is.", good)
    assert nc.translate_article("AAA up", "x", "fr", "AAA", client, "m")[0] == "AAA en hausse"


def test_row_holds_both_languages(monkeypatch):
    monkeypatch.setattr(nc, "translate_article", lambda t, c, to, *a: (f"[{to}] {t}", f"[{to}] {c}"))
    v = {}
    row = nc._both_languages("Titre", "Texte", "fr", "AAA", None, "m", v)
    assert row == ["Titre", "Texte", "[en] Titre", "[en] Texte"]      # title_fr, content_fr, title_en, content_en
    assert v["translated"] is True
    assert len(nc.NEWS_COLUMNS) == 11
