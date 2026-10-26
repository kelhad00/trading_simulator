"""The chart toolbar's "Reset axes" and "Autoscale" buttons (supervisor, 2026-10-26).

- Reset axes: back to the view of the start of the simulation (the whole session
  width, prices fitted) and follow the new candles again, also while paused.
- Autoscale: fit the candles shown, and keep fitting them on every update instead
  of going back to the starting view.

Plotly sends the same autorange for both buttons; Reset also sends showspikes
(checked in a browser with plotly.js 2.23.2)."""
import time
from types import SimpleNamespace

import pytest
from dash import no_update
from dash.exceptions import PreventUpdate

import trade.callbacks.dashboard.graph as graph

AUTOSCALE = {"xaxis.autorange": True, "yaxis.autorange": True}
RESET = {"xaxis.autorange": True, "xaxis.showspikes": False,
         "yaxis.autorange": True, "yaxis.showspikes": False}


def press(monkeypatch, relayout, trigger="company-graph"):
    monkeypatch.setattr(graph, "ctx", SimpleNamespace(triggered_id=trigger))
    return graph.track_graph_auto_follow(relayout, "AAA")


def test_autoscale_keeps_fitting_the_candles(monkeypatch):
    assert press(monkeypatch, AUTOSCALE) == (False, None, no_update)


def test_reset_follows_again_and_redraws_at_once(monkeypatch):
    follow, manual_range, redraw = press(monkeypatch, RESET)
    assert (follow, manual_range) == (True, None)
    assert redraw is not no_update


def test_zoom_or_pan_is_pinned(monkeypatch):
    assert press(monkeypatch, {"xaxis.range[0]": 3, "xaxis.range[1]": 12}) == (False, [3, 12], no_update)


def test_window_resize_and_company_switch_follow(monkeypatch):
    assert press(monkeypatch, {"autosize": True}) == (True, None, no_update)
    assert press(monkeypatch, None, trigger="company-selector") == (True, None, no_update)


def test_other_changes_are_ignored(monkeypatch):
    with pytest.raises(PreventUpdate):
        press(monkeypatch, {"dragmode": "zoom"})


def draw(market_df, monkeypatch, trigger, follow, redraw=None):
    monkeypatch.setattr(graph, "ctx", SimpleNamespace(triggered_id=trigger))
    return graph.update_graph(1, "AAA", market_df.index[30], time.time(), 15, 0, [], "light", follow, None,
                              100_000, None, 1, 20, graph_redraw=redraw)


def test_autoscaled_chart_sends_no_range(market_df, monkeypatch):
    """No range from the app: Plotly keeps fitting the candles shown."""
    fig = draw(market_df, monkeypatch, "periodic-updater", False)[1]
    assert fig.layout.xaxis.range is None
    assert fig.layout.yaxis.range is None


def test_reset_redraw_shows_the_starting_view_without_moving_time(market_df, monkeypatch):
    out = draw(market_df, monkeypatch, "graph-redraw", True, redraw=123.0)
    fig = out[1]
    assert out[0] == market_df.index[30]                         # time didn't move
    assert list(fig.layout.xaxis.range) == [-0.5, 159.5]         # the whole session width
    assert fig.layout.yaxis.range is not None                    # prices fitted
    assert "123.0" in fig.layout.xaxis.uirevision                # new revision: applied even while paused
