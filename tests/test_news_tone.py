"""News generation: wrong tone, company not named or wrong language -> rewrite (up to 3 tries); still wrong -> kept and marked
needs_review; the "fits the price curve" word check alone never causes a rewrite.

The AI and the tone checker are replaced by stand-ins: no AI credit is used and
nothing is written to the real news file."""
from types import SimpleNamespace

import pandas as pd
import pytest

import trade.utils.news_generation.news_creation as nc


def check(tone_ok=True, company=True, language=True, curve=True, confidence=0.9):
    """A verification result like verify_article returns."""
    return {"tone_ok": tone_ok, "tone_confidence": confidence, "model_label": "positive" if tone_ok else "negative",
            "company_mentioned": company, "curve_score": 5 if curve else 0, "curve_ok": curve,
            "language_ok": language, "grade": "A" if all((tone_ok, company, language, curve)) else "C",
            "passed": all((tone_ok, company, language, curve)), "flagged": False,
            "sentiment_label": ("strong " if confidence >= 0.75 else "weak ") + ("positive" if tone_ok else "negative")}


def run(results):
    """Feed the retry rule a sequence of check results; return (title, verification, versions written)."""
    written = []

    def write():
        written.append(f"version {len(written) + 1}")
        return written[-1], "text"

    feed = iter(results)
    title, _, v = nc._write_checked_article(write, lambda t, c: next(feed), "test")
    return title, v, len(written)


def test_right_first_time_is_written_once():
    title, v, n = run([check()])
    assert (title, n, v["attempts"], v["needs_review"]) == ("version 1", 1, 1, False)


def test_wrong_tone_is_rewritten_until_right():
    title, v, n = run([check(tone_ok=False), check(tone_ok=False), check()])
    assert title == "version 3" and n == 3 and v["tone_ok"] and not v["needs_review"]


def test_still_wrong_after_three_tries_is_kept_and_marked_for_review():
    title, v, n = run([check(tone_ok=False, confidence=0.9),
                       check(tone_ok=False, confidence=0.6),     # least sure it's negative: best of three
                       check(tone_ok=False, confidence=0.8)])
    assert n == nc.MAX_ATTEMPTS == 3
    assert v["needs_review"] and title == "version 2"


def test_curve_word_check_alone_never_causes_a_rewrite():
    title, v, n = run([check(curve=False)])
    assert n == 1 and not v["needs_review"] and v["curve_ok"] is False      # score still recorded


def test_company_not_named_also_gets_up_to_three_tries():
    title, v, n = run([check(company=False), check(company=False), check(company=False)])
    assert n == 3 and v["needs_review"]


def test_wrong_language_is_rewritten_until_right():
    title, v, n = run([check(language=False), check()])
    assert title == "version 2" and n == 2 and not v["needs_review"]


# ── Whole generator, with stand-ins ─────────────────────────────────────────

class FakeAI:
    def __init__(self):
        self.prompts = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, messages, model):
        self.prompts.append(messages[0]["content"])
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=f"Text {len(self.prompts)}"))])


@pytest.fixture
def generator(fake_data, monkeypatch):
    ai = FakeAI()
    monkeypatch.setattr(nc, "_build_client", lambda *a, **k: (ai, "fake-model"))
    monkeypatch.setattr(nc, "load_data", lambda path: pd.DataFrame(
        {"content": ["Good reference.", "Bad reference."], "sentiment": ["positive", "negative"]}))
    return ai


def test_generator_rewrites_an_ambiguous_positive_article_and_keeps_the_good_version(generator, monkeypatch):
    results = iter([check(tone_ok=False), check(tone_ok=False), check(),   # positive: ambiguous twice, then good
                    check(tone_ok=True)])                                    # negative: right first time
    monkeypatch.setattr(nc, "verify_article", lambda *a, **k: next(results))
    news, report = nc.create_news("AAA", "AAA", "Tech", "linear", "en", ([110], [115]), "fake-model")

    positive = report[0]
    assert positive["attempts"] == 3 and not positive["needs_review"]
    assert news.iloc[0]["sentiment_label"] == "strong positive"              # the label of the kept version
    assert report[1]["attempts"] == 1
    assert len(news) == 2                                                    # no article lost


def test_positive_prompts_warn_against_negative_sounding_words(generator):
    nc.transform_news_content("ref", "AAA", "Tech", "linear", "en", generator, "m", "positive")
    nc.transform_news_content("ref", "AAA", "Tech", "linear", "fr", generator, "m", "positive")
    nc.transform_news_content("ref", "AAA", "Tech", "linear", "en", generator, "m", "negative")
    en_pos, fr_pos, en_neg = generator.prompts
    assert "efficiency drives" in en_pos and "GOOD news for AAA" in en_pos
    assert "BONNE nouvelle pour AAA" in fr_pos
    assert "efficiency drives" not in en_neg                                 # negative news unchanged
