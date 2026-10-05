"""Automatic news (after confirming charts) reports how it ended instead of failing silently.

The AI is replaced by stand-ins, so nothing is generated or written."""
import httpx
import pytest
from dash.exceptions import PreventUpdate
from openai import APIConnectionError

import trade.callbacks.settings.charts.modal as modal

COMPANIES = {"AAA": {"label": "AAA"}}


@pytest.fixture
def run_job(monkeypatch):
    monkeypatch.setattr(modal, "get_news_position_for_companies", lambda *a, **k: {})

    def run(create_news, lang="en", provider="groq"):
        monkeypatch.setattr(modal, "create_news_for_companies", create_news)
        job = f"test-{lang}-{provider}"
        modal._AUTO_NEWS_JOBS[job] = {"status": "running", "lang": lang, "companies": "AAA"}
        with pytest.raises(PreventUpdate):           # still running: no pop-up yet
            modal.report_auto_news(1, job)
        modal._auto_generate_news(job, COMPANIES, "random", 2, 2, 0.5, 3, 0, lang, provider, "http://x", "key")
        notification, timer_off, job_after = modal.report_auto_news(2, job)
        assert timer_off is True and job_after is None and job not in modal._AUTO_NEWS_JOBS
        return notification
    return run


def test_success_shows_a_green_news_ready_message(run_job):
    n = run_job(lambda *a, **k: {"total": 4, "passed": 4, "flagged": 0})
    assert n.color == "green" and "News ready for AAA" in n.message


def test_flagged_articles_show_an_orange_message(run_job):
    n = run_job(lambda *a, **k: {"total": 4, "passed": 3, "flagged": 1}, lang="fr")
    assert n.color == "orange" and "Actualités prêtes" in n.message


def test_connection_problem_shows_a_red_message_with_the_reason(run_job):
    def no_connection(*a, **k):
        raise APIConnectionError(request=httpx.Request("POST", "http://x"))
    n = run_job(no_connection)
    assert n.color == "red" and "Could not connect to Groq" in n.message


def test_unknown_job_just_stops_checking():
    assert modal.report_auto_news(1, "does-not-exist")[1:] == (True, None)
