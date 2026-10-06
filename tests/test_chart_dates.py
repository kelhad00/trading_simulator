"""Dates on the chart axis: a readable number (at most 8) of the candles on screen,
also when zoomed in, at round spacings, and never a future date."""
import pandas as pd
import pytest

from trade.utils.graph import candlestick_charts as charts


def draw(market_df, shown, view_range=None):
    """Chart of AAA with `shown` candles revealed; returns the dates on the axis."""
    df = market_df["AAA"]
    ts = df.index[shown - 1]
    fig, _ = charts.create_graph(df, ts, False, 10, follow=view_range is None, view_range=view_range)
    return list(fig.layout.xaxis.tickvals), [str(i) for i in df.index]


@pytest.mark.parametrize("candles, step", [(16, 2), (40, 5), (56, 7), (100, 14), (520, 90)])
def test_round_spacing_keeps_at_most_eight_dates(candles, step):
    assert charts._date_label_step(candles) == step
    assert candles / step <= charts.MAX_DATE_LABELS


def test_zoomed_in_on_a_few_candles_shows_several_dates(market_df):
    ticks, labels = draw(market_df, shown=110, view_range=[90.5, 106.5])    # 16 candles on screen
    assert len(ticks) >= 5
    positions = [labels.index(t) for t in ticks]
    assert all(91 <= p <= 106 for p in positions)                          # only dates on screen


def test_whole_session_view_spreads_few_dates(market_df):
    ticks, labels = draw(market_df, shown=150)
    assert 2 <= len(ticks) <= charts.MAX_DATE_LABELS


def test_no_future_date_is_ever_labelled(market_df):
    for view in (None, [100.5, 159.5]):
        ticks, labels = draw(market_df, shown=120, view_range=view)
        assert all(labels.index(t) < 120 for t in ticks)


def test_dates_stay_in_place_as_candles_are_added(market_df):
    before, _ = draw(market_df, shown=120)
    after, _ = draw(market_df, shown=121)
    assert set(before) <= set(after)                                       # old labels don't move


def test_unreadable_zoom_value_falls_back_to_the_whole_session(market_df):
    labels = [str(i) for i in market_df.index]
    assert charts._slots_in_view(["not-a-date", None], labels) == (0, len(labels) - 1)
