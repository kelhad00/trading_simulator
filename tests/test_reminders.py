"""Time reminders ("5 minutes remaining"...) can be switched on or off in
Settings -> News -> Notifications, like the news notifications."""
import io
import json
import time
import zipfile

import pytest
from dash.exceptions import PreventUpdate

import trade.callbacks.dashboard.reminders as reminders
import trade.callbacks.settings.news as news_settings
from trade.utils.session import build_session_zip, extract_session_zip

FOURTEEN_MIN_AGO = time.time() - 14 * 60      # in a 15-minute session: 1 minute left


def fire(enabled):
    return reminders.fire_time_reminders(1, "ts", FOURTEEN_MIN_AGO, 15, 0, [], enabled)


def test_reminders_appear_when_switched_on():
    popups, shown = fire(True)
    assert len(popups) > 0 and "1min" in shown


def test_no_reminders_when_switched_off():
    with pytest.raises(PreventUpdate):
        fire(False)


def test_reminders_are_on_when_nothing_is_saved_yet():
    popups, _ = fire(None)
    assert len(popups) > 0


def test_switch_always_shows_the_saved_setting():
    assert news_settings.show_reminders_setting(False) is False
    assert news_settings.show_reminders_setting(True) is True
    assert news_settings.show_reminders_setting(None) is True        # default: on


def test_flipping_the_switch_saves_the_setting():
    assert news_settings.save_reminders_setting(False) is False
    assert news_settings.save_reminders_setting(True) is True


def test_setting_is_kept_in_session_files(fake_data, tmp_path):
    raw = build_session_zip({}, 100_000, 10, 5000, str(fake_data), reminders_enabled=False)
    assert extract_session_zip(raw, str(tmp_path))["reminders-enabled"] is False


def test_old_session_files_keep_reminders_on(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("session.json", json.dumps({"version": 1, "stores": {
            "companies": {}, "initial-cashflow": 100_000, "max-requests": 10, "update-time": 5000}}))
    assert extract_session_zip(buf.getvalue(), str(tmp_path))["reminders-enabled"] is True
