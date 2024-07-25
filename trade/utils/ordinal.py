def ordinal(n, lang):
    if lang == "en":
        return "%d%s" % (n, "tsnrhtdd"[((n // 10 % 10 != 1) * (n % 10 < 4) * n % 10)::4])
    if lang == "fr":
        return "%d%s" % (n, "er" if n == 1 else "eme")