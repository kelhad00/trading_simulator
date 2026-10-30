"""Money put aside for waiting buy orders (audit #4 and #5, 30 Oct 2026).

#4: editing a waiting buy order to a price the participant can't afford even one
share at used to be accepted, and the cash went below zero.
#5: the end-of-session results ignored the money put aside for buy orders still
waiting, so they showed a loss that never happened.
"""
import pytest

import trade.callbacks.dashboard.request as request
import trade.callbacks.reset as reset
from trade.utils import leaderboard as lb


def _texts(component):
    """Every text shown inside a Dash component tree."""
    if isinstance(component, (str, int, float)):
        return [str(component)]
    children = getattr(component, "children", None)
    if children is None:
        return []
    if not isinstance(children, (list, tuple)):
        children = [children]
    return [text for child in children for text in _texts(child)]


# ── #4: editing a waiting order never makes the cash negative ──────────────

def test_too_expensive_price_keeps_the_order_and_the_cash():
    # 100€ in total: all of it put aside for 1 share at 100€, 0€ left
    order = {"action": "buy", "shares": 1, "company": "AAA", "price": 100.0}
    requests, cash = request.edit_request_values([1_000.0], [1], ["buy"], [dict(order)], {}, 0)
    assert requests[0]["price"] == 100.0 and requests[0]["shares"] == 1   # kept as it was
    assert cash is request.no_update                                     # still 0€, not -900€


def test_too_expensive_switch_from_sell_to_buy_is_refused():
    order = {"action": "sell", "shares": 1, "company": "AAA", "price": 100.0}
    requests, cash = request.edit_request_values([100.0], [1], ["buy"], [dict(order)], {"AAA": 1}, 50)
    assert requests[0]["action"] == "sell"
    assert cash is request.no_update


def test_affordable_new_price_still_works():
    order = {"action": "buy", "shares": 1, "company": "AAA", "price": 100.0}
    requests, cash = request.edit_request_values([150.0], [1], ["buy"], [dict(order)], {}, 100)
    assert requests[0]["price"] == 150.0
    assert cash == pytest.approx(50)


def test_too_many_shares_are_still_cut_to_what_the_money_buys():
    order = {"action": "buy", "shares": 1, "company": "AAA", "price": 100.0}
    requests, cash = request.edit_request_values([100.0], [10], ["buy"], [dict(order)], {}, 200)
    assert requests[0]["shares"] == 3                                    # 300€ in total
    assert cash == pytest.approx(0)


def test_an_order_already_too_expensive_is_left_alone():
    # Saved before the fix with negative cash: no endless redraw
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": 100.0}
    requests, cash = request.edit_request_values([100.0], [10], ["buy"], [dict(order)], {}, -2_000)
    assert requests is request.no_update and cash is request.no_update


# ── #5: the results count the money put aside ──────────────────────────────

def test_results_count_money_put_aside_for_a_waiting_order():
    # 100 000€ at the start, a 20 000€ buy order never executed
    order = {"action": "buy", "shares": 200, "company": "AAA", "price": 100.0}
    content = reset.display_pnl_summary(True, 80_000, {}, {}, 100_000, {}, "en", [order])
    texts = _texts(content)
    assert "100 000.00 €" in texts                    # final value, not 80 000
    assert "+0.00 %" in texts                         # nothing lost, not -20 %


def test_results_agree_with_the_portfolio_and_the_leaderboard():
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": 100.0, "fee": 1}
    totals = {"BBB": 5_000.0}
    expected = lb.total_assets(93_990, totals, [order])               # 100 000
    content = reset.display_pnl_summary(True, 93_990, totals, {"BBB": 5}, 100_000, {}, "en", [order])
    assert f"{expected:,.2f} €".replace(",", " ") in _texts(content)


def test_waiting_sell_orders_add_nothing():
    order = {"action": "sell", "shares": 5, "company": "BBB", "price": 1_000.0}
    content = reset.display_pnl_summary(True, 95_000, {"BBB": 5_000.0}, {"BBB": 5}, 100_000, {}, "en", [order])
    assert "100 000.00 €" in _texts(content)


def test_results_without_waiting_orders_are_as_before():
    content = reset.display_pnl_summary(True, 90_000, {"BBB": 12_000.0}, {"BBB": 5}, 100_000, {}, "en")
    texts = _texts(content)
    assert "102 000.00 €" in texts and "+2.00 %" in texts
