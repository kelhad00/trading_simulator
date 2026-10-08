"""Each participant keeps their own language, even when several participants use
the same server. The language used to be one value shared by everyone on the
server (dash.page_registry['lang']): a participant opening the app in English
switched the others to English too, and the logs could record the wrong chart tab.
Now the callbacks read the language from the participant's own page address
(?lang=en, State("url", "search")), which is different in each browser."""
import glob
import os

import trade.callbacks.dashboard.request as request
import trade.callbacks.dashboard.reminders as reminders
from trade.locales import language, translations as tls
from trade.utils.export import format_charts_type

TRADE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "trade")


def test_two_participants_get_their_own_language_at_the_same_time():
    # Same moment, same server: one in French, one in English
    _, fr = request.add_request([], "AAA", "buy", 0, 1, 100, None, {}, 10, "fr")
    _, en = request.add_request([], "AAA", "buy", 0, 1, 100, None, {}, 10, "en")
    assert fr == tls["fr"]["err-wrong-form"] and en == tls["en"]["err-wrong-form"]
    _, fr_again = request.add_request([], "AAA", "buy", 0, 1, 100, None, {}, 10, "fr")
    assert fr_again == tls["fr"]["err-wrong-form"]          # the English one didn't switch it


def test_time_reminders_in_the_participants_language():
    import time
    started = time.time() - 14 * 60                          # 15-min session: 1 min left
    popups_en, _ = reminders.due_reminders(started, 15, 0, [], True, "en")
    popups_fr, _ = reminders.due_reminders(started, 15, 0, [], True, "fr")
    assert popups_en[-1].message == tls["en"]["notifications"]["reminder-1min"]
    assert popups_fr[-1].message == tls["fr"]["notifications"]["reminder-1min"]


def test_unknown_or_missing_language_is_french():
    assert language("en") == "en" and language("fr") == "fr"
    assert language(None) == "fr" and language("xx") == "fr"


def test_logs_record_the_chart_tab_whatever_the_language():
    assert format_charts_type(tls["fr"]["tab-market"]) == "market"
    assert format_charts_type(tls["en"]["tab-market"]) == "market"
    assert format_charts_type(tls["fr"]["tab-revenue"]) == "revenue"
    assert format_charts_type(tls["en"]["tab-revenue"]) == "revenue"


def test_language_comes_from_the_participants_page_address():
    assert language("?lang=en") == "en"
    assert language("?lang=fr") == "fr"
    assert language("?company=AAA&lang=en") == "en"
    assert language("") == "fr" and language("?company=AAA") == "fr"      # no ?lang= : French, like the pages


def test_no_code_uses_the_shared_server_language_any_more():
    for path in glob.glob(os.path.join(TRADE, "**", "*.py"), recursive=True):
        if f"{os.sep}venv{os.sep}" in path:
            continue
        source = open(path, encoding="utf-8").read()
        assert "page_registry" not in source, (
            f"{path}: use the participant's address (State('url', 'search') + trade.locales.language) "
            "instead of a language shared by everyone on the server")
