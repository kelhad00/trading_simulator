"""Where a session starts (history candles) and the Settings -> Advanced page."""
import pytest
from dash.exceptions import PreventUpdate

from trade.utils.market import get_start_timestamp
import trade.callbacks.reset as reset
import trade.callbacks.settings.advanced as advanced


def test_session_starts_after_100_history_candles_by_default(market_df):
    assert get_start_timestamp(market_df) == market_df.index[100]


def test_history_candles_setting_moves_the_start(market_df):
    assert get_start_timestamp(market_df, 50) == market_df.index[50]


def test_too_big_a_number_does_not_break_the_start(market_df):
    assert get_start_timestamp(market_df, 99_999) == market_df.index[-1]


def test_reset_goes_back_to_the_chosen_start(market_df, monkeypatch):
    monkeypatch.setattr(reset, "_archive_exports", lambda *a, **k: None)   # don't move log files
    assert reset.reset_data(1, 100_000, 0, {}, 50)[0] == market_df.index[50]
    assert reset.reset_data(1, 100_000, 0, {}, None)[0] == market_df.index[100]


def test_changing_the_setting_before_a_session_moves_the_start(market_df):
    timestamp, candle_step = reset.apply_initial_bars(50, None)
    assert timestamp == market_df.index[50] and candle_step is None


def test_changing_the_setting_never_moves_a_running_session(fake_data):
    with pytest.raises(PreventUpdate):
        reset.apply_initial_bars(50, 1_790_000_000.0)


VALUES = (5000, 10, 100_000, 15, "S", "4", 50)   # update time ... steps, history candles


@pytest.mark.parametrize("search, title", [("?lang=en", "Settings updated"), ("?lang=fr", "Paramètres mis à jour")])
def test_saving_settings_shows_the_right_message(search, title):
    out = advanced.update_advanced_settings(1, *VALUES, search)
    assert out[-1].title == title
    assert out[:7] == (5000, 10, 100_000, 15, "S", 4, 50)


def test_empty_field_is_refused_with_an_error():
    out = advanced.update_advanced_settings(1, *VALUES[:-1], None, "?lang=en")
    assert out[-1].title == "Error" and out[6] is advanced.no_update
