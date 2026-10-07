"""Each session's logs go to their own folder with a session ID, so participants'
logs never mix, even if Reset is forgotten or two sessions run at the same time."""
import csv
import json
import re
from pathlib import Path

import pytest
from dash.exceptions import PreventUpdate

from trade.defaults import defaults as dlt
from trade.utils import export
import trade.callbacks.dashboard.export as export_callbacks
import trade.callbacks.reset as reset


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def log_a_buy(session_id, company="AAA"):
    export.export_data("2025-01-05", [], 100_000, {company: 1}, {company: 100.0}, company, None,
                       "market", "buy", max_requests=1, session_id=session_id)
    export.log_session_event("session-start", "2025-01-05", 100_000, company, session_id)


def test_session_id_is_date_time_and_unique():
    ids = {export.new_session_id() for _ in range(50)}
    assert len(ids) == 50
    assert all(re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_[0-9a-f]{4}", i) for i in ids)


def test_two_sessions_never_share_a_file(fake_data):
    log_a_buy("2026-10-07_10-15_aaaa", "AAA")
    log_a_buy("2026-10-07_10-15_bbbb", "BBB")
    for sid, company in (("2026-10-07_10-15_aaaa", "AAA"), ("2026-10-07_10-15_bbbb", "BBB")):
        folder = Path(dlt.data_path) / "exports" / sid
        interface = rows(folder / "interface-logs.csv")
        assert interface[0][:2] == ["uuid", "session-id"]
        assert {r[1] for r in interface[1:]} == {sid}                 # only this session's rows
        assert {r[interface[0].index("selected-company")] for r in interface[1:]} == {company}
        assert (folder / "portfolio-logs.csv").exists() and (folder / "request-logs.csv").exists()
    assert not (Path(dlt.data_path) / "export").exists()             # nothing in the shared folder


def test_log_info_lives_in_the_session_folder(fake_data):
    export.write_log_info({"steps_per_candle": 4}, "2026-10-07_10-15_cccc")
    info = json.loads((Path(dlt.data_path) / "exports" / "2026-10-07_10-15_cccc" / "log-info.json").read_text("utf-8"))
    assert info["session_id"] == "2026-10-07_10-15_cccc" and info["log_format_version"] == 3


def test_without_a_session_id_logs_still_go_somewhere(fake_data):
    log_a_buy(None)                                                  # an older page: nothing lost
    assert (Path(dlt.data_path) / "export" / "interface-logs.csv").exists()


def test_opening_the_dashboard_gives_the_tab_a_session():
    sid = export_callbacks.give_tab_a_session_id("/dashboard", None)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_[0-9a-f]{4}", sid)


@pytest.mark.parametrize("pathname, session_id", [("/dashboard", "already-one"), ("/", None), ("/settings", None)])
def test_refresh_keeps_the_session_and_other_pages_start_none(pathname, session_id):
    with pytest.raises(PreventUpdate):
        export_callbacks.give_tab_a_session_id(pathname, session_id)


def test_reset_starts_a_new_session(fake_data, monkeypatch):
    monkeypatch.setattr(reset, "_archive_exports", lambda *a, **k: None)
    first = reset.reset_data(1, 100_000, 0, {}, None)[-1]
    second = reset.reset_data(1, 100_000, 0, {}, None)[-1]
    assert first and second and first != second
    assert reset.reset_modal(1, 100_000, 0, {}, None)[-1] not in (first, second)
