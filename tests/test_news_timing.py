"""When news appears: never before its own day (no extra day early), and with moving
candles at its step inside the candle. The news list and the pop-ups agree.

Fake data: one candle per day from 1 Jan 2025 (00:00); news dated 10-14 Jan at 09:00."""
import pandas as pd
import pytest

import trade.callbacks.dashboard.news as news
from trade.utils import news_timing as nt


def day(d):
    return f"2025-01-{d:02d} 00:00:00+01:00"


def shown_titles(timestamp, candle_step=None, steps=1):
    table, _ = news.cb_update_news_table(timestamp, candle_step, None, steps)
    rows = table.children[1].children
    return [r.children[0].children[1] for r in rows]


def test_news_never_appears_the_day_before_its_date(fake_data):
    assert "AAA beats expectations" not in shown_titles(day(9))      # 10 Jan news, on 9 Jan
    assert "AAA beats expectations" in shown_titles(day(10))


def test_moving_candles_news_appears_at_its_step(fake_data):
    # 09:00 = 37.5% of the day -> step 2 of 4 (the 15/30/45/60 steps of the candle)
    assert "AAA beats expectations" not in shown_titles(day(10), candle_step=1, steps=4)
    assert "AAA beats expectations" in shown_titles(day(10), candle_step=2, steps=4)
    assert "AAA beats expectations" in shown_titles(day(10), candle_step=None, steps=4)   # candle closed


def test_article_dated_at_candle_start_gets_the_same_step_for_everyone(market_df):
    df = pd.DataFrame({"date": pd.to_datetime(["2025-01-10 00:00"] * 3),
                       "title": ["Alpha news", "Beta news", "Gamma news"]})
    first = nt.article_positions(df, market_df.index, 4).tolist()
    nt._candle_cache.clear()
    assert nt.article_positions(df, market_df.index, 4).tolist() == first          # same every time
    assert all(c == 9 and 1 <= s <= 4 for c, s in first)                          # 10 Jan, a step 1..4


def test_steps_off_news_appears_with_its_candle(market_df):
    df = pd.DataFrame({"date": pd.to_datetime(["2025-01-10 09:00"]), "title": ["x"]})
    assert nt.article_positions(df, market_df.index, 1).tolist() == [(9, 1)]


def notify(timestamp, step, last_seen, steps=4, offset=0):
    return news.notify_new_news(timestamp, step, last_seen, {}, None, offset, True, steps)


def test_popup_appears_at_the_same_moment_as_the_list(fake_data):
    _, seen = notify(day(10), 1, None)                     # first time: only records where we are
    popups, seen = notify(day(10), 1, seen)
    assert popups is news.no_update                        # step 1: not yet
    popups, seen = notify(day(10), 2, seen)
    assert popups is not news.no_update and len(popups) == 1   # step 2: "AAA beats expectations"
    popups, _ = notify(day(10), 3, seen)
    assert popups is news.no_update                        # not repeated


def test_warn_me_early_setting_still_looks_ahead(fake_data):
    _, seen = notify(day(9), 4, None, offset=1)            # 9 Jan + 1 day ahead
    popups, _ = notify(day(10), 1, [8, 4], offset=1)       # now looking at 11 Jan step 1
    assert popups is not news.no_update                    # 10 Jan news announced in advance


def test_old_saved_value_restarts_quietly(fake_data):
    popups, seen = notify(day(12), 1, "2025-01-13 00:00:00")   # date text from the old version
    assert popups is news.no_update and isinstance(seen, list)
