"""Smoother screen: every update the browser receives makes it redraw the whole
screen, so a tick sends as few updates as possible. The chart update also carries
the clock label, the news clock, the revenue year and the time reminders, and the
other parts of the screen are only woken when something really changed."""
import time
from types import SimpleNamespace

import pytest

import trade.callbacks.dashboard.graph as graph
import trade.callbacks.dashboard.request as request
from trade.utils import news_timing as nt
from trade.utils.news import get_news_dataframe

# Output positions of update_graph
TIMER, NEWS_CLOCK, REVENUE_YEAR, POPUPS, SHOWN = 6, 7, 8, 9, 10


def tick(market_df, monkeypatch, i, news_clock=None, revenue_year=None, started=None, reminders=True):
    """One timer tick of update_graph, with the session at candle number i."""
    monkeypatch.setattr(graph, "ctx", SimpleNamespace(triggered_id="periodic-updater"))
    return graph.update_graph(1, "AAA", market_df.index[i], started or time.time(), 15, 0, [], "light", True, None,
                              100_000, None, 1, 100, 2000, 10, 100_000, {}, "session-1",
                              news_clock, revenue_year, 0, [], reminders)


# ── The 0 / 0.0 fix ──────────────────────────────────────────────────────────

def test_whole_numbers_from_the_browser_are_not_a_change(market_df):
    # The browser sends back 0 for 0.0: that used to count as a change on every tick
    shares, totals_seen_by_browser = {"AAA": 0, "BBB": 0}, {"AAA": 0, "BBB": 0}
    out = request.execute_requests([], market_df.index[110], 2, shares, 100_000, totals_seen_by_browser, {}, {}, 4)
    assert out[3] is request.no_update


def test_a_real_change_is_still_sent(market_df):
    out = request.execute_requests([], market_df.index[110], 2, {"AAA": 10, "BBB": 0}, 100_000,
                                   {"AAA": 0, "BBB": 0}, {}, {}, 4)
    assert out[3] is not request.no_update and out[3]["AAA"] > 0


# ── News clock ───────────────────────────────────────────────────────────────

def test_news_count_goes_up_exactly_when_an_article_appears(market_df):
    news_df = get_news_dataframe()
    count = lambda day, step: nt.appeared_count(news_df, market_df.index, 4, (day - 1, step))
    assert count(10, 1) == 0          # 10 Jan, 09:00 news: not yet at 15 min
    assert count(10, 2) == 1          # ... appeared at step 2 (like the news list)
    assert count(13, 4) == 4
    assert count(30, 1) == 5          # all 5 fake articles


def test_tick_wakes_the_news_only_when_an_article_appeared(market_df, monkeypatch):
    out = tick(market_df, monkeypatch, 8)                                  # 9 Jan -> 10 Jan: 1 article
    assert out[NEWS_CLOCK] == ["session-1", 1, 1]
    out = tick(market_df, monkeypatch, 9, news_clock=out[NEWS_CLOCK])      # 10 -> 11 Jan: 1 more
    assert out[NEWS_CLOCK] == ["session-1", 2, 2]
    out = tick(market_df, monkeypatch, 100, news_clock=["session-1", 5, 5])  # nothing new
    assert out[NEWS_CLOCK] is graph.no_update


def test_a_new_session_wakes_the_news_again(market_df, monkeypatch):
    out = tick(market_df, monkeypatch, 100, news_clock=["old-session", 5, 5])
    assert out[NEWS_CLOCK] == ["session-1", 5, 5]


# ── Clock label, revenue year, reminders ─────────────────────────────────────

def test_clock_label_comes_with_the_chart(market_df, monkeypatch):
    out = tick(market_df, monkeypatch, 100)
    assert out[0] == market_df.index[101]                                  # the chart moved on
    assert out[TIMER] == graph.timer_label(market_df.index[101], None, 1)


def test_revenue_chart_is_only_woken_by_a_new_year(market_df, monkeypatch):
    assert tick(market_df, monkeypatch, 100, revenue_year=None)[REVENUE_YEAR] == 2025      # page just opened
    assert tick(market_df, monkeypatch, 100, revenue_year=2025)[REVENUE_YEAR] is graph.no_update


def test_time_reminders_come_with_the_chart(market_df, monkeypatch):
    fourteen_min_ago = time.time() - 14 * 60                              # 15-min session: 1 min left
    out = tick(market_df, monkeypatch, 100, started=fourteen_min_ago)
    assert out[POPUPS] is not graph.no_update and "1min" in out[SHOWN]


def test_no_time_reminders_when_switched_off(market_df, monkeypatch):
    out = tick(market_df, monkeypatch, 100, started=time.time() - 14 * 60, reminders=False)
    assert out[POPUPS] is graph.no_update and out[SHOWN] is graph.no_update


# ── Guard: nothing else listens to the timer ─────────────────────────────────

def test_only_the_chart_update_listens_to_the_timer():
    import dash._callback as dash_callbacks
    import trade.app  # noqa: F401  (registers every callback of the app)

    on_timer = [c["output"] for c in dash_callbacks.GLOBAL_CALLBACK_LIST
                if any(i["id"] == "periodic-updater" for i in c["inputs"])]
    assert len(on_timer) == 1 and "company-graph.figure" in on_timer[0], (
        "Another part of the screen is woken on every tick: send it with update_graph instead")
