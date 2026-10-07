"""The app must work without internet in the lab: the styling (Tailwind) and the
icons are files in trade/assets/, never downloaded when a page opens."""
import glob
import json
import os
import re
import sys

from conftest import ROOT

TRADE = os.path.join(ROOT, "trade")
ASSETS = os.path.join(TRADE, "assets")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fetch_icons  # noqa: E402


def app_python_files():
    for path in glob.glob(os.path.join(TRADE, "**", "*.py"), recursive=True):
        if f"{os.sep}venv{os.sep}" not in path:
            yield path


def test_no_scripts_or_styles_are_loaded_from_the_internet():
    import trade.app as app
    assert app.external_scripts == []
    assert not app.app.config.external_stylesheets
    for path in app_python_files():
        source = open(path, encoding="utf-8").read()
        assert "cdn." not in source and "unpkg.com" not in source and "jsdelivr" not in source, path


def tailwind_selector(css_class):
    """How Tailwind writes a class name in the CSS file (special characters escaped)."""
    return "." + re.sub(r"([\[\]/:.%#(),])", lambda m: "\\" + m.group(1), css_class)


def test_every_style_class_used_is_in_the_local_tailwind_file():
    css = open(os.path.join(ASSETS, "tailwind.css"), encoding="utf-8").read()
    used = set()
    for path in app_python_files():
        for classes in re.findall(r"className\s*=\s*['\"]([^'\"]*)['\"]", open(path, encoding="utf-8").read()):
            used |= set(classes.split())
    missing = sorted(c for c in used if tailwind_selector(c) not in css)
    assert not missing, (f"Rebuild trade/assets/tailwind.css (README, 'Working offline'); missing: {missing}")


def test_every_icon_used_is_in_the_local_icon_file():
    js = open(os.path.join(ASSETS, "icons.js"), encoding="utf-8").read()
    preload = json.loads(js.split("window.IconifyPreload = ", 1)[1].rsplit(";", 1)[0])
    saved = {(s["prefix"], name) for s in preload for name in list(s["icons"]) + list(s.get("aliases", {}))}
    used = {(prefix, name) for prefix, names in fetch_icons.icons_used_in_code().items() for name in names}
    missing = sorted(f"{p}:{n}" for p, n in used - saved)
    assert not missing, (f"Run tools/fetch_icons.py (README, 'Working offline'); missing: {missing}")
