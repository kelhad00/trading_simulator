from urllib.parse import parse_qs

from .fr import translation as french
from .en import translation as english

translations = {**french, **english}


def language(lang):
    """The participant's own language, French if unknown.

    `lang` is a language code ("en") or the participant's page address part
    ("?lang=en", State("url", "search")), which every page has. Never a value
    shared on the server: two participants in two languages on the same server
    would otherwise switch each other's language."""
    if isinstance(lang, str) and "=" in lang:
        lang = (parse_qs(lang.lstrip("?")).get("lang") or [None])[0]
    return lang if lang in translations else "fr"
