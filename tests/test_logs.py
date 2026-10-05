"""Research logs: values always stay under the right column, writers never mix, each
session records its code version and settings."""
import csv
import json
import threading

import pandas as pd
import pytest

from trade.utils import export


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def portfolio_row(companies, value):
    row = {"uuid": f"u{value}"}
    row.update({f"{c}-shares": value for c in companies})
    return pd.DataFrame([row])


def test_rows_with_the_same_columns_are_simply_added(tmp_path):
    path = tmp_path / "portfolio-logs.csv"
    export.save_df(portfolio_row(["AAA", "BBB"], 1), str(path))
    export.save_df(portfolio_row(["AAA", "BBB"], 2), str(path))
    assert read_rows(path) == [["uuid", "AAA-shares", "BBB-shares"], ["u1", "1", "1"], ["u2", "2", "2"]]


def test_when_companies_change_every_value_stays_under_its_company(tmp_path):
    path = tmp_path / "portfolio-logs.csv"
    export.save_df(portfolio_row(["AAA", "BBB", "CCC"], 1), str(path))     # 3 companies
    export.save_df(portfolio_row(["BBB", "DDD"], 2), str(path))             # list changed
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    assert list(df.columns) == ["uuid", "AAA-shares", "BBB-shares", "CCC-shares", "DDD-shares"]
    assert df.iloc[0].tolist() == ["u1", "1", "1", "1", ""]
    assert df.iloc[1].tolist() == ["u2", "", "2", "", "2"]
    assert all(len(r) == 5 for r in read_rows(path))                       # no misaligned row


def test_damaged_old_file_is_left_untouched_and_new_rows_go_to_a_new_part(tmp_path):
    path = tmp_path / "portfolio-logs.csv"
    damaged = "uuid,AAA-shares\nu1,1\nu2,2,9,9\n"                           # a row longer than its header
    path.write_text(damaged, encoding="utf-8")
    export.save_df(portfolio_row(["AAA", "BBB"], 3), str(path))
    assert path.read_text(encoding="utf-8") == damaged
    assert read_rows(tmp_path / "portfolio-logs-2.csv") == [["uuid", "AAA-shares", "BBB-shares"], ["u3", "3", "3"]]


def test_writers_at_the_same_moment_never_mix_their_lines(tmp_path):
    path = tmp_path / "interface-logs.csv"
    row = pd.DataFrame([{"uuid": "x" * 40, "form-action": "buy", "is_news_description_displayed": False}])

    def writer():
        for _ in range(25):
            export.save_df(row, str(path))

    threads = [threading.Thread(target=writer) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    rows = read_rows(path)
    assert len(rows) == 1 + 8 * 25
    assert all(r == ["x" * 40, "buy", "False"] for r in rows[1:])


def test_each_session_records_code_version_and_settings(fake_data):
    export.write_log_info({"steps_per_candle": 4, "companies": ["AAA"]})
    export.write_log_info({"steps_per_candle": 1, "companies": ["AAA", "BBB"]})
    info = json.loads((fake_data / "export" / "log-info.json").read_text(encoding="utf-8"))
    assert info["log_format_version"] == export.LOG_FORMAT_VERSION
    assert [s["settings"]["steps_per_candle"] for s in info["sessions"]] == [4, 1]
    assert all(s["tradesim_version"] and s["started_at"] for s in info["sessions"])


def test_starting_a_session_writes_log_info_automatically(market_df, monkeypatch):
    from pathlib import Path
    from types import SimpleNamespace
    import trade.callbacks.dashboard.graph as graph
    from trade.defaults import defaults as dlt

    export_dir = Path(dlt.data_path) / "export"
    export_dir.mkdir()
    monkeypatch.setattr(graph, "ctx", SimpleNamespace(triggered_id="periodic-updater"))
    graph.update_graph(1, "AAA", market_df.index[100], None, 15, 0, [], "light", True, None, 100_000,
                       None, 4, 100, 2000, 10, 100_000,
                       {"AAA": {"got_charts": True}, "BBB": {"got_charts": True}, "CCC": {"got_charts": False}})
    info = json.loads((export_dir / "log-info.json").read_text(encoding="utf-8"))
    settings = info["sessions"][0]["settings"]
    assert settings["steps_per_candle"] == 4 and settings["update_time_ms"] == 2000
    assert settings["companies"] == ["AAA", "BBB"]          # only companies with charts


# ── Rename alarm ─────────────────────────────────────────────────────────────
# Researchers' analysis depends on these names. If one of these tests fails,
# a log column was renamed or removed: only do that on purpose, then update
# the expected names here and raise LOG_FORMAT_VERSION in trade/utils/export.py.

INTERFACE_COLUMNS = ["uuid", "market-timestamp", "host-timestamp", "cashflow", "selected-company",
                     "form-action", "chart-type", "is_news_description_displayed", "news_title"]


@pytest.fixture
def export_folder(fake_data):
    (fake_data / "export").mkdir()
    return fake_data / "export"


def test_log_column_names_are_unchanged(export_folder):
    export.export_data("2025-01-05", [{"action": "buy", "shares": 3, "company": "AAA", "price": 101.5}],
                       100_000, {"AAA": 3, "BBB": 0}, {"AAA": 300.0, "BBB": 0.0}, "AAA", None,
                       "market", "buy", max_requests=2)
    export.log_session_event("session-start", "2025-01-05", 100_000, "AAA")

    assert read_rows(export_folder / "interface-logs.csv")[0] == INTERFACE_COLUMNS
    assert read_rows(export_folder / "portfolio-logs.csv")[0] == [
        "uuid", "AAA-shares", "BBB-shares", "AAA-totals", "BBB-totals"]
    assert read_rows(export_folder / "request-logs.csv")[0] == [
        "uuid", "deleted-request", "request-1", "request-2"]
    assert all(len(r) == len(INTERFACE_COLUMNS) for r in read_rows(export_folder / "interface-logs.csv"))
