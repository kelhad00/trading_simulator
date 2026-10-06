"""The news checker (FinBERT) needs extra packages. When they are missing, nothing is
silently passed: a clear warning, articles marked needs_review, and the pop-up says so.
Runs with stand-ins: no AI and no FinBERT are used."""
import os
from types import SimpleNamespace

import pandas as pd
import pytest

import trade.utils.news_generation.verify as verify
import trade.utils.news_generation.news_creation as nc
import trade.callbacks.settings.charts.modal as modal
from conftest import ROOT


@pytest.fixture
def checker_missing(monkeypatch):
    """Pretend transformers and torch are not installed."""
    real = verify.importlib.util.find_spec
    monkeypatch.setattr(verify.importlib.util, "find_spec",
                        lambda name, *a: None if name in verify.CHECKER_PACKAGES else real(name, *a))
    monkeypatch.setattr(verify, "_worker_available", None)
    monkeypatch.setattr(verify, "_worker_proc", None)


def test_missing_packages_are_named(checker_missing):
    assert verify.missing_checker_packages() == ["transformers", "torch"]
    assert "transformers" in verify.checker_problem()


def test_missing_packages_give_a_loud_warning_without_trying_to_start(checker_missing, monkeypatch, capsys):
    monkeypatch.setattr(verify.subprocess, "Popen", lambda *a, **k: pytest.fail("should not try to start"))
    assert verify._get_sentiment_worker() is False
    out = capsys.readouterr().out
    assert "NEWS CHECKER UNAVAILABLE" in out and "requirements-news.txt" in out


def test_unchecked_article_is_marked_for_review_not_passed():
    unchecked = {"tone_ok": True, "tone_confidence": 0.0, "model_label": "unavailable",
                 "company_mentioned": True, "curve_score": 5, "curve_ok": True, "language_ok": True,
                 "grade": "B", "passed": True, "flagged": False, "sentiment_label": "neutral"}
    _, _, v = nc._write_checked_article(lambda: ("t", "c"), lambda t, c: unchecked, "test")
    assert v["needs_review"] is True and v["attempts"] == 1     # no pointless rewrites


def test_generation_counts_unchecked_articles(fake_data, checker_missing, monkeypatch):
    ai = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=lambda messages, model: SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Text"))]))))
    monkeypatch.setattr(nc, "_build_client", lambda *a, **k: (ai, "fake-model"))
    dataset = pd.DataFrame({"content": ["Good.", "Bad."], "sentiment": ["positive", "negative"]})
    real_load = nc.load_data
    monkeypatch.setattr(nc, "load_data", lambda path, *a: dataset if path.endswith("news_dataset.csv") else real_load(path, *a))
    companies = {"AAA": {"label": "AAA", "activity": "Tech", "got_charts": True}}
    stats = nc.create_news_for_companies(companies, {"AAA": ([110], [115])}, "en")
    assert stats["total"] == 2 and stats["unchecked"] == 2 and stats["passed"] == 0


def test_popup_warns_when_articles_were_not_checked():
    job = "test-unchecked"
    modal._AUTO_NEWS_JOBS[job] = {"status": "done", "lang": "en", "companies": "AAA",
                                  "stats": {"total": 2, "passed": 0, "flagged": 2, "unchecked": 2}}
    popup, _, _ = modal.report_auto_news(1, job)
    assert popup.color == "orange" and "NOT checked" in popup.message and popup.autoClose is False


def test_news_requirements_list_the_checker_packages():
    text = open(os.path.join(ROOT, "requirements-news.txt"), encoding="utf-8").read()
    for package in verify.CHECKER_PACKAGES:
        assert package in text
