"""Leaderboard: the participant against 20 robot traders made from the app's own prices,
ranked by total assets, shown only when switched on in Settings -> Advanced."""
import io
import json
import zipfile

import plotly

import trade.callbacks.dashboard.leaderboard as board
import trade.callbacks.settings.advanced as advanced_settings
from trade.utils import leaderboard as lb
from trade.utils.market import get_market_dataframe, get_start_timestamp
from trade.utils.session import build_session_zip, extract_session_zip

MONEY = 100_000
COMPANIES = {"AAA": {"got_charts": True}, "BBB": {"got_charts": True}}


def prices():
    return get_market_dataframe().xs('Close', axis=1, level=1)


# ── Robots ────────────────────────────────────────────────────────────────

def test_robots_start_with_the_starting_money(fake_data):
    robots = lb.robot_assets(prices(), 100, MONEY)
    assert robots.shape[1] == 20
    assert (robots.iloc[0].round(2) == MONEY).all()


def test_one_row_per_candle_from_the_session_start(fake_data):
    assert len(lb.robot_assets(prices(), 100, MONEY)) == len(prices()) - 100


def test_robots_follow_the_market(fake_data):
    robots = lb.robot_assets(prices(), 100, MONEY)
    assert not (robots.iloc[-1].round(2) == MONEY).all()


def test_same_robots_for_every_participant(fake_data):
    assert lb.robot_assets(prices(), 100, MONEY).equals(lb.robot_assets(prices(), 100, MONEY))


def test_company_whose_data_stops_keeps_its_last_price(fake_data):
    # BBB has no data after day 120: the robots' values must stay numbers
    assert not lb.robot_assets(prices(), 100, MONEY).isna().any().any()


def test_robots_follow_the_starting_money(fake_data):
    assert (lb.robot_assets(prices(), 100, 50_000).iloc[0].round(2) == 50_000).all()


def test_robots_at_a_moment_of_the_session(fake_data):
    df = get_market_dataframe()
    start = get_start_timestamp(df, 100)
    assert len(lb.robots_at(df, df.index[110], start, MONEY, COMPANIES)) == 20
    assert lb.robots_at(df, df.index[50], start, MONEY, COMPANIES) == {}     # before the session
    assert lb.robots_at(df, "not a date", start, MONEY, COMPANIES) == {}


# ── Ranking ───────────────────────────────────────────────────────────────

def test_ranking_order_and_my_rank():
    table, my_rank = lb.ranking({"Trader 1": 120.0, "Trader 2": 80.0}, 100.0)
    assert [name for _, name, _ in table] == ["Trader 1", lb.YOU, "Trader 2"]
    assert my_rank == 2


def test_equal_totals_share_a_rank():
    # At the very start everyone has the starting money: all first, "You" listed first
    table, my_rank = lb.ranking({"Trader 1": 100.0, "Trader 2": 100.0}, 100.0)
    assert my_rank == 1
    assert [rank for rank, _, _ in table] == [1, 1, 1]
    assert table[0][1] == lb.YOU


def test_total_assets_counts_cash_reserved_buys_and_shares():
    requests = [{"action": "buy", "shares": 2, "price": 10.0}, {"action": "sell", "shares": 1, "price": 99.0}]
    assert lb.total_assets(1000, {"AAA": 500.0, "BBB": None}, requests) == 1520


# ── Dashboard box ─────────────────────────────────────────────────────────

def show(fake_data, enabled=True, cashflow=MONEY, totals=None, day=110):
    df = get_market_dataframe()
    style, children = board.update_leaderboard(df.index[day], totals or {}, cashflow, [], enabled,
                                               100, MONEY, COMPANIES, "?lang=en")
    return style, json.loads(json.dumps(children, cls=plotly.utils.PlotlyJSONEncoder))


def my_rank_line(children):
    return children["props"]["children"][1]["props"]["children"]


def test_switched_off_the_box_is_hidden(fake_data):
    style, children = show(fake_data, enabled=False)
    assert style == {"display": "none"}
    assert children is None


def test_switched_on_shows_top_5_and_my_rank(fake_data):
    style, children = show(fake_data)
    assert style["display"] == "flex"
    assert style["maxHeight"] == "40%"        # never squashes the portfolio above
    rows = children["props"]["children"][0]["props"]["children"][1]["props"]["children"]
    assert len(rows) == 5
    assert my_rank_line(children).startswith("My rank:")
    assert "/ 21" in my_rank_line(children)


def test_more_money_means_a_better_rank(fake_data):
    _, poor = show(fake_data, cashflow=1)
    _, rich = show(fake_data, cashflow=10 * MONEY)
    assert my_rank_line(poor).startswith("My rank: 21")
    assert my_rank_line(rich).startswith("My rank: 1 ")


# ── Setting ───────────────────────────────────────────────────────────────

def test_switch_is_off_by_default_and_saves():
    assert advanced_settings.show_leaderboard_setting("advanced", None) is False
    assert advanced_settings.show_leaderboard_setting("advanced", True) is True
    assert advanced_settings.save_leaderboard_setting(True) is True
    assert advanced_settings.save_leaderboard_setting(None) is False


def test_setting_is_kept_in_session_files(fake_data, tmp_path):
    raw = build_session_zip({}, MONEY, 10, 5000, str(fake_data), leaderboard_enabled=True)
    assert extract_session_zip(raw, str(tmp_path))["leaderboard-enabled"] is True


def test_old_session_files_have_no_leaderboard(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("session.json", json.dumps({"version": 1, "stores": {
            "companies": {}, "initial-cashflow": MONEY, "max-requests": 10, "update-time": 5000}}))
    assert extract_session_zip(buf.getvalue(), str(tmp_path))["leaderboard-enabled"] is False
