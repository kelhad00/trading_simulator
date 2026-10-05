"""Every text exists in both English and French."""
from trade.locales import translations as tls


def keys(tree, prefix=""):
    found = set()
    for k, v in tree.items():
        found.add(prefix + str(k))
        if isinstance(v, dict):
            found |= keys(v, f"{prefix}{k}.")
    return found


def test_english_and_french_have_the_same_texts():
    en, fr = keys(tls["en"]), keys(tls["fr"])
    assert en - fr == set(), f"missing in French: {sorted(en - fr)}"
    assert fr - en == set(), f"missing in English: {sorted(fr - en)}"


def test_no_text_is_left_empty():
    def empty(tree, prefix=""):
        out = []
        for k, v in tree.items():
            if isinstance(v, dict):
                out += empty(v, f"{prefix}{k}.")
            elif isinstance(v, str) and not v.strip():
                out.append(prefix + str(k))
        return out
    assert empty(tls["en"]) == [] and empty(tls["fr"]) == []
