"""Commission fees: N% paid on every executed buy and sell (Settings -> Advanced).

With a 0.05% fee, buying 100€ of shares costs 100.05€ and selling 100€ of shares
brings in 99.95€. With 0% (the default) every number is the same as before."""
import io
import json
import zipfile
from types import SimpleNamespace

import pytest

import trade.callbacks.dashboard.request as request
import trade.callbacks.settings.advanced as advanced
from trade.utils import fees, leaderboard as lb
from trade.utils.market import get_market_dataframe
from trade.utils.session import build_session_zip, extract_session_zip


# ── The fee itself ────────────────────────────────────────────────────────

def test_supervisor_example_buy_and_sell_100_euros():
    assert fees.buy_cost(1, 100, 0.05) == pytest.approx(100.05)
    assert fees.sell_proceeds(1, 100, 0.05) == pytest.approx(99.95)


def test_no_fee_changes_nothing():
    assert fees.buy_cost(3, 100, 0) == 300
    assert fees.sell_proceeds(3, 100, 0) == 300
    assert fees.buy_cost(3, 100, None) == 300                 # nothing saved yet


def test_most_shares_money_can_buy_includes_the_fee():
    assert fees.max_buy_shares(1000, 100, 0) == 10
    assert fees.max_buy_shares(1000, 100, 1) == 9             # 10 shares would cost 1010€


def test_old_orders_without_a_fee_put_aside_only_the_price():
    assert fees.reserved({"action": "buy", "shares": 2, "price": 50}) == 100
    assert fees.reserved({"action": "sell", "shares": 2, "price": 50, "fee": 1}) == 0


# ── Placing, executing, cancelling ───────────────────────────────────────

def place(cash, fee_pct, pct=100, price=100.0):
    return request.process_submit_button(1, "AAA", "buy", price, pct, cash, None, {"AAA": 0}, [], 10, "?lang=en", fee_pct)


def test_placing_a_buy_puts_aside_price_and_fee():
    req, _, cash = place(1000, 1, pct=50)                     # 500€ -> 4 shares (5 would cost 505€)
    assert req[-1]["shares"] == 4
    assert req[-1]["fee"] == 1
    assert cash == pytest.approx(1000 - 404)


def test_cash_never_goes_below_zero_when_buying_with_everything():
    _, _, cash = place(1000, 1, pct=100)
    assert cash >= 0


def test_not_enough_money_for_price_and_fee_is_refused():
    error, _ = request.add_request([], "AAA", "buy", 100, 10, 1000, None, {"AAA": 0}, 10, "en", fee_pct=1)
    assert error is True                                      # 10 shares + 1% = 1010€ > 1000€


def fill(order, cash, held, market_df, day=110):
    """Execute `order` on a candle where it surely fills (limit far away)."""
    out = request.execute_requests([order], market_df.index[day], None, {"AAA": held, "BBB": 0}, cash,
                                   {"AAA": 0.0, "BBB": 0.0}, {}, {}, 1)
    price = request.current_price("AAA", market_df.index[day], None, 1)
    return out, price


def test_executed_buy_pays_market_price_plus_fee(market_df):
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": 1_000.0, "fee": 0.05}
    cash_after_placing = 100_000 - fees.reserved(order)
    out, price = fill(order, cash_after_placing, 0, market_df)
    assert out[2] == pytest.approx(100_000 - 10 * price * 1.0005)          # unused deposit comes back
    assert out[4]["AAA"] == pytest.approx(10 * price * 1.0005)             # Px Achat includes the fee


def test_executed_sell_receives_market_price_minus_fee(market_df):
    order = {"action": "sell", "shares": 10, "company": "AAA", "price": 0.01, "fee": 0.05}
    out, price = fill(order, 0, 10, market_df)
    assert out[2] == pytest.approx(10 * price * 0.9995)
    assert out[5]["AAA"]["revenue"] == pytest.approx(10 * price)           # Px Vente = price sold at


def test_with_no_fee_orders_execute_exactly_as_before(market_df):
    buy = {"action": "buy", "shares": 10, "company": "AAA", "price": 1_000.0, "fee": 0}
    out, price = fill(buy, 100_000 - 10_000, 0, market_df)
    assert out[2] == pytest.approx(100_000 - 10 * price)


@pytest.mark.parametrize("button", ["one", "all"])
def test_cancelling_gives_back_price_and_fee(button, monkeypatch):
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": 100.0, "fee": 1}
    trigger = "clear-done-btn" if button == "all" else {"type": "requests-selectable-table", "index": 0}
    monkeypatch.setattr(request, "ctx", SimpleNamespace(triggered_id=trigger))
    _, cash = request.remove_request(1, [1], [dict(order)], 0)
    assert cash == pytest.approx(1010)                        # nothing bought: no fee kept


def test_editing_an_order_keeps_its_own_fee():
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": 100.0, "fee": 1}
    requests, cash = request.edit_request_values([100.0], [5], ["buy"], [dict(order)], {}, 0)
    assert requests[0]["shares"] == 5
    assert cash == pytest.approx(1010 - 505)


def test_total_assets_counts_the_fee_put_aside():
    order = {"action": "buy", "shares": 10, "company": "AAA", "price": 100.0, "fee": 1}
    assert lb.total_assets(98_990, {}, [order]) == pytest.approx(100_000)


# ── Leaderboard robots pay the fee too ───────────────────────────────────

def test_robots_pay_the_fee_on_their_purchase(fake_data):
    prices = get_market_dataframe().xs('Close', axis=1, level=1)
    no_fee = lb.robot_assets(prices, 100, 100_000).iloc[0]
    with_fee = lb.robot_assets(prices, 100, 100_000, fee_pct=1).iloc[0]
    assert (with_fee < no_fee).all()
    assert (no_fee - with_fee).max() < 1_000                  # at most 1% of the money


# ── Setting ───────────────────────────────────────────────────────────────

VALUES = (5000, 10, 100_000, 15, "S", "4", 50)


def test_saving_the_fee():
    out = advanced.update_advanced_settings(1, *VALUES, "?lang=en", 0.05)
    assert out[7] == 0.05


@pytest.mark.parametrize("bad", [None, -1, 50])
def test_empty_or_out_of_range_fee_is_refused(bad):
    out = advanced.update_advanced_settings(1, *VALUES, "?lang=en", bad)
    assert out[7] is advanced.no_update
    assert out[-1].title == "Error"


def test_fee_is_kept_in_session_files(fake_data, tmp_path):
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data), commission_fee=0.05)
    assert extract_session_zip(raw, str(tmp_path))["commission-fee"] == 0.05


def test_old_session_files_have_no_fee(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("session.json", json.dumps({"version": 1, "stores": {
            "companies": {}, "initial-cashflow": 100_000, "max-requests": 10, "update-time": 5000}}))
    assert extract_session_zip(buf.getvalue(), str(tmp_path))["commission-fee"] == 0
