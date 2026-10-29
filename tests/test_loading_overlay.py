"""Configurator: while Dash is busy, an "Updating..." screen covers the page so the
researcher cannot click a half-drawn page. The Runtime never gets it (it updates on
every tick and the participant must be able to trade)."""


def test_configurator_gets_the_loading_screen_in_both_languages():
    import trade.app as app
    html = app._loading_overlay('config')
    assert 'id="loading-overlay"' in html
    assert 'Updating…' in html and 'Mise à jour…' in html
    assert "'" + app.UPDATE_TITLE + "'" in html     # it watches the title Dash really sets


def test_runtime_gets_no_loading_screen():
    import trade.app as app
    assert app._loading_overlay('runtime') == ''


def test_dash_shows_the_watched_title_while_busy():
    import trade.app as app
    assert app.app.config.update_title == app.UPDATE_TITLE
