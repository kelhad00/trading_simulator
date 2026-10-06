"""Cash belongs to one participant's game: a new tab starts with the starting money,
and a game in progress is never changed (even on a page refresh)."""
import os
import re

import pytest
from dash.exceptions import PreventUpdate

import trade.callbacks.reset as reset
from conftest import ROOT

NO_SHARES = {"AAA": 0, "BBB": 0}


def test_cash_is_kept_per_tab_like_shares_and_orders():
    app_py = open(os.path.join(ROOT, "trade", "app.py"), encoding="utf-8").read()
    for store in ("cashflow", "portfolio-shares", "requests"):
        match = re.search(rf"dcc\.Store\(id=['\"]{store}['\"][^\n]*storage_type=['\"](\w+)['\"]", app_py)
        assert match and match.group(1) == "session", f"{store} should be kept per tab"


def test_new_tab_starts_with_the_starting_money():
    # previous participant's cash would be 80 000; this tab has no game yet
    assert reset.start_cash_for_new_tab(100_000, None, [], NO_SHARES, 80_000) == 100_000


def test_imported_starting_amount_is_respected():
    assert reset.start_cash_for_new_tab(50_000, None, [], NO_SHARES, 100_000) == 50_000


def test_running_session_is_never_changed():
    with pytest.raises(PreventUpdate):
        reset.start_cash_for_new_tab(100_000, 1_790_000_000.0, [], NO_SHARES, 80_000)


def test_waiting_order_or_shares_held_keep_the_cash():
    order = [{"company": "AAA", "action": "buy", "price": 100.0, "shares": 10}]
    with pytest.raises(PreventUpdate):
        reset.start_cash_for_new_tab(100_000, None, order, NO_SHARES, 99_000)
    with pytest.raises(PreventUpdate):
        reset.start_cash_for_new_tab(100_000, None, [], {"AAA": 5, "BBB": 0}, 99_500)


def test_nothing_sent_when_cash_is_already_right():
    with pytest.raises(PreventUpdate):
        reset.start_cash_for_new_tab(100_000, None, [], NO_SHARES, 100_000)
