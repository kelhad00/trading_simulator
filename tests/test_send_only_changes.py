"""Faster screen: on a tick where nothing changed, nothing is sent to the browser."""
from types import SimpleNamespace

import pytest
from dash.exceptions import PreventUpdate

import trade.callbacks.dashboard.news as news
import trade.callbacks.dashboard.portfolio as portfolio
import trade.callbacks.dashboard.request as request
from trade.utils import candle_steps as cs

NOW = "2025-01-20 00:00:00"


def test_news_list_is_sent_once_then_only_when_it_changes(fake_data):
    table, key = news.cb_update_news_table(1, NOW)
    assert table is not news.no_update
    assert news.cb_update_news_table(2, NOW, key) == (news.no_update, news.no_update)   # quiet tick


def test_news_list_is_sent_again_when_new_news_arrives(fake_data):
    _, key = news.cb_update_news_table(1, "2025-01-11 00:00:00")      # 2 news so far
    table, new_key = news.cb_update_news_table(2, NOW, key)          # 5 news now
    assert table is not news.no_update and new_key != key


def test_news_list_is_drawn_when_the_page_opens(fake_data):
    table, _ = news.cb_update_news_table(1, NOW, None)                # page memory starts empty
    assert table is not news.no_update


@pytest.mark.parametrize("show", [portfolio.display_portfolio_updated, portfolio.display_portfolio_table_updated])
def test_portfolio_ignores_the_timer_alone(show, monkeypatch):
    monkeypatch.setattr(portfolio, "ctx", SimpleNamespace(triggered_id="periodic-updater"))
    args = {portfolio.display_portfolio_updated: (1, {"AAA": 0.0}, 100_000, [], 100_000),
            portfolio.display_portfolio_table_updated: (1, {"AAA": 0.0}, {"AAA": 0}, "AAA", {}, {})}[show]
    with pytest.raises(PreventUpdate):
        show(*args)


def test_portfolio_redraws_when_its_values_change(monkeypatch):
    monkeypatch.setattr(portfolio, "ctx", SimpleNamespace(triggered_id="portfolio-totals"))
    cash, investment = portfolio.display_portfolio_updated(1, {"AAA": 500.0}, 100_000, [], 100_000)
    assert "100500" in str(investment)


def test_quiet_tick_sends_no_portfolio_values(market_df):
    shares = {"AAA": 0, "BBB": 0}
    totals = {"AAA": 0.0, "BBB": 0.0}
    out = request.execute_requests([], market_df.index[110], 2, dict(shares), 100_000, dict(totals), {}, {}, 4)
    assert all(o is request.no_update for o in out)


def test_company_without_a_price_does_not_count_as_a_change(market_df):
    ts = market_df.index[130]                 # BBB has no data any more: its value is NaN
    first = request.execute_requests([], ts, 2, {"AAA": 0, "BBB": 0}, 100_000, {"AAA": 0.0, "BBB": 0.0}, {}, {}, 4)
    seen_by_browser = {k: (None if v != v else v) for k, v in first[3].items()}   # NaN arrives as empty
    again = request.execute_requests([], ts, 2, {"AAA": 0, "BBB": 0}, 100_000, seen_by_browser, {}, {}, 4)
    assert again[3] is request.no_update


def test_holding_shares_sends_the_new_value_when_the_price_moves(market_df):
    ts = market_df.index[110]
    before = {"AAA": 10 * cs.current_price("AAA", ts, 1, 4), "BBB": 0.0}
    out = request.execute_requests([], ts, 2, {"AAA": 10, "BBB": 0}, 100_000, before, {}, {}, 4)
    assert out[3] is not request.no_update
    assert out[3]["AAA"] == pytest.approx(10 * cs.current_price("AAA", ts, 2, 4))
