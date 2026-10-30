"""Saving and loading session.zip keeps the settings; old files still load as before."""
import io
import json
import zipfile

from trade.defaults import defaults as dlt
from trade.utils.session import build_session_zip, extract_session_zip


def test_new_session_file_keeps_its_settings(fake_data, tmp_path_factory):
    raw = build_session_zip({"AAA": {"label": "AAA"}}, 50_000, 10, 2000, str(fake_data),
                            steps_per_candle=4, initial_bars=50)
    stores = extract_session_zip(raw, str(tmp_path_factory.mktemp("load")))
    assert stores["steps-per-candle"] == 4
    assert stores["initial-bars"] == 50
    assert stores["initial-cashflow"] == 50_000
    assert stores["companies"] == {"AAA": {"label": "AAA"}}


def test_old_session_file_without_new_settings_plays_as_before(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("session.json", json.dumps({"version": 1, "stores": {
            "companies": {}, "initial-cashflow": 100_000, "max-requests": 10, "update-time": 5000}}))
    stores = extract_session_zip(buf.getvalue(), str(tmp_path))
    assert stores["steps-per-candle"] == 1                       # finished candles, as before
    assert stores["initial-bars"] == dlt.initial_reveal_bars     # 100 history candles, as before


def test_loading_copies_the_data_files(fake_data, tmp_path_factory):
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data))
    target = tmp_path_factory.mktemp("load")
    extract_session_zip(raw, str(target))
    assert (target / "generated_data.csv").exists() and (target / "news.csv").exists()


def test_revenue_data_reaches_the_participant_computer(fake_data, tmp_path_factory):
    """The zip looked for "revenues.csv", a file that never exists: the revenue data
    never reached the participants' computers (found in the audit, fixed 30 Oct 2026)."""
    (fake_data / "revenue.csv").write_text("symbol,AAA\nasOfDate,2024-12-31\nTotalRevenue,1000\n", encoding="utf-8")
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data))
    assert "revenue.csv" in zipfile.ZipFile(io.BytesIO(raw)).namelist()
    target = tmp_path_factory.mktemp("participant")             # a clean participant computer
    extract_session_zip(raw, str(target))
    assert (target / "revenue.csv").read_text(encoding="utf-8") == (fake_data / "revenue.csv").read_text(encoding="utf-8")


def test_notification_settings_reach_the_participant_computer(fake_data, tmp_path):
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data), notif_filter=["negative"], notif_offset=2)
    stores = extract_session_zip(raw, str(tmp_path))
    assert stores["notif-filter"] == ["negative"]
    assert stores["notif-offset"] == 2


def test_old_session_files_keep_the_default_notification_settings(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("session.json", json.dumps({"version": 1, "stores": {
            "companies": {}, "initial-cashflow": 100_000, "max-requests": 10, "update-time": 5000}}))
    stores = extract_session_zip(buf.getvalue(), str(tmp_path))
    assert stores["notif-filter"] == ["positive", "negative", "neutral"]
    assert stores["notif-offset"] == 0


def test_every_setting_saved_in_the_configurator_is_in_the_session_file():
    """Each participant uses their own computer: a setting missing from session.zip is
    silently replaced by its default there. Every local store the Configurator writes
    must be exported and imported."""
    import re
    from pathlib import Path
    trade = Path(__file__).resolve().parents[1] / "trade"
    settings_code = "".join(p.read_text(encoding="utf-8") for p in (trade / "callbacks" / "settings").rglob("*.py"))
    written = set(re.findall(r'Output\(\s*["\']([\w-]+)["\']\s*,\s*["\']data["\']', settings_code))
    app_code = (trade / "app.py").read_text(encoding="utf-8")
    local = set(re.findall(r'dcc\.Store\(id=["\']([\w-]+)["\'][^)]*storage_type=["\']local["\']', app_code))
    exported = set(json.loads(zipfile.ZipFile(io.BytesIO(build_session_zip({}, 1, 1, 1, str(trade))))
                              .read("session.json"))["stores"])
    import_code = (trade / "callbacks" / "home_import.py").read_text(encoding="utf-8")
    imported = set(re.findall(r'Output\(\s*["\']([\w-]+)["\']\s*,\s*["\']data["\']', import_code))
    settings = (written & local) - {"companies"}               # companies: exported, set elsewhere
    assert settings - exported == set(), "saved in the Configurator but not exported"
    assert settings - imported == set(), "exported but not imported on the participant's computer"


def test_import_returns_one_value_per_setting(fake_data):
    """Adding a setting means adding an Output AND a returned value in home_import.py:
    if the counts differ, Dash refuses the answer and the import does nothing."""
    import base64
    import re
    from pathlib import Path
    import trade.callbacks.home_import as home_import
    code = (Path(__file__).resolve().parents[1] / "trade" / "callbacks" / "home_import.py").read_text(encoding="utf-8")
    head = code[:code.index("def import_session(")]
    outputs = re.findall(r'Output\(\s*["\']([\w-]+)["\']', head[head.rindex("@callback"):])
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data), candle_path="random", chart_buttons_enabled=True)
    good = home_import.import_session("data:application/zip;base64," + base64.b64encode(raw).decode(), "s.zip", "?lang=en")
    assert len(good) == len(outputs)
    assert dict(zip(outputs, good))["candle-path"] == "random"
    assert dict(zip(outputs, good))["chart-buttons-enabled"] is True
    assert len(home_import.import_session("data:application/zip;base64,AAAA", "x.zip", "?lang=en")) == len(outputs)
    assert len(home_import.import_session(None, None, None)) == len(outputs)
