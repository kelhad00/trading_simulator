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
