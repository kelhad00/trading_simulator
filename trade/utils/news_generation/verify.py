import re
import os
import sys
import json
import subprocess
import functools

print = functools.partial(print, flush=True)

# ── FinBERT subprocess worker ─────────────────────────────────────────────────
# PyTorch's c10.dll fails to initialise on some Windows environments when loaded
# inside an existing process. Running FinBERT in a dedicated child process avoids
# this completely — the child loads torch on its own main thread with a clean
# process context.

_worker_proc = None
_worker_available = None   # True / False / None (not yet tried)

_WORKER_SCRIPT = os.path.join(os.path.dirname(__file__), "_finbert_worker.py")


def _get_finbert():
    """
    Start the FinBERT worker subprocess if not already running.
    Returns True if the worker is ready, False if it could not be started.
    """
    global _worker_proc, _worker_available

    if _worker_available is False:
        return False
    if _worker_proc is not None and _worker_proc.poll() is None:
        return True   # already running

    try:
        print("[VERIFY] Starting sentiment worker (FinBERT + DistilCamemBERT)...")
        _worker_proc = subprocess.Popen(
            [sys.executable, _WORKER_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        # Block until the worker prints READY (model loaded)
        ready_line = _worker_proc.stdout.readline().strip()
        if ready_line == "READY":
            print("[VERIFY] Sentiment worker ready (FinBERT=EN, DistilCamemBERT=FR).")
            _worker_available = True
            return True
        raise RuntimeError(f"Unexpected worker output: {ready_line!r}")
    except Exception as e:
        print(f"[VERIFY] WARNING: FinBERT worker could not be started ({e}). Tone check will be skipped.")
        _worker_available = False
        return False


# ── Curve vocabulary (weighted per profile) ───────────────────────────────────
# Each key is a stem/word; value is its weight (1–3).
# An article must accumulate CURVE_PASS_THRESHOLD points to pass curve fit.

CURVE_VOCABULARY = {
    'crash': {
        # English
        'collapse': 3, 'collaps': 3, 'plunge': 3, 'plummet': 3,
        'decline': 3, 'falls': 3, 'fell': 3, 'falling': 3, 'fallen': 3,
        'crisis': 2, 'slump': 2, 'deteriorat': 2, 'loss': 2,
        'tumble': 2, 'drop': 2, 'shrink': 2, 'shrinking': 2,
        'weak': 1, 'concern': 1, 'cautious': 1, 'warning': 1, 'fear': 1,
        # French
        'effondrement': 3, 'effondr': 3, 'chute': 3, 'plongeon': 3,
        'déclin': 3, 'baisse': 3, 'recul': 3, 'dégringol': 3,
        'crise': 2, 'perte': 2, 'détérior': 2, 'repli': 2,
        'faible': 1, 'inquiétude': 1, 'prudence': 1, 'avertissement': 1, 'crainte': 1,
    },
    'exponential': {
        # English
        'surge': 3, 'surging': 3, 'surged': 3, 'skyrocket': 3,
        'explosive': 3, 'accelerat': 3, 'soar': 3, 'soaring': 3,
        'rapid': 2, 'dramatic': 2, 'momentum': 2, 'record': 2,
        'outperform': 2, 'exceed': 2, 'exceptional': 2,
        'strong': 1, 'remarkable': 1,
        # French
        'explosion': 3, 'explosif': 3, 'envolée': 3, 'flambée': 3,
        'accélérat': 3, 'fulgur': 3, 'spectaculaire': 3,
        'rapide': 2, 'exceptionnel': 2, 'record': 2, 'dynamisme': 2,
        'fort': 1, 'remarquable': 1, 'impressionnant': 1,
    },
    'linear': {
        # English
        'steady': 3, 'stable': 3, 'consistent': 3,
        'gradual': 2, 'sustained': 2, 'regular': 2, 'moderate': 2,
        'reliable': 1, 'predictable': 1, 'solid': 1,
        # French
        'régulier': 3, 'régulière': 3, 'stable': 3, 'constant': 3,
        'progressif': 2, 'progressive': 2, 'soutenu': 2, 'modéré': 2,
        'linéaire': 3, 'continu': 2, 'continue': 2,
        'fiable': 1, 'solide': 1, 'prévisible': 1,
    },
    'logarithmic': {
        # English
        'matur': 3, 'plateau': 3, 'stabiliz': 3,
        'decelerat': 2, 'consolidat': 2, 'slow': 2, 'saturat': 2,
        'modest': 1, 'taper': 2, 'level': 1,
        # French
        'maturité': 3, 'plateau': 3, 'stabilisation': 3, 'stabilise': 3,
        'décélérat': 2, 'consolidat': 2, 'ralentissement': 2, 'saturat': 2,
        'modeste': 1, 'tassement': 2, 'plafond': 2,
    },
    'volatile': {
        # English
        'volatil': 3, 'unpredictable': 3, 'erratic': 3,
        'swing': 2, 'fluctuat': 2, 'uncertain': 2,
        'turbulent': 2, 'unstable': 2, 'oscillat': 2,
        'sharp': 1, 'sudden': 1,
        # French
        'volatil': 3, 'imprévisible': 3, 'erratique': 3,
        'fluctuat': 2, 'incertain': 2, 'turbulent': 2,
        'instable': 2, 'oscillat': 2, 'capricieux': 2,
        'brusque': 1, 'soudain': 1,
    },
}

CURVE_PASS_THRESHOLD = 4


# ── Stopword sets for language detection ──────────────────────────────────────

_EN_STOPWORDS = {
    'the', 'is', 'are', 'and', 'in', 'of', 'to', 'a', 'that', 'it',
    'for', 'on', 'with', 'as', 'at', 'by', 'an', 'be', 'was', 'has',
    'have', 'had', 'its', 'this', 'from', 'or', 'but', 'not', 'been',
    'which', 'their', 'will', 'would', 'could', 'should', 'they',
}

_FR_STOPWORDS = {
    'le', 'la', 'les', 'est', 'et', 'en', 'de', 'du', 'un', 'une',
    'dans', 'que', 'qui', 'il', 'elle', 'au', 'aux', 'par', 'sur',
    'son', 'sa', 'ses', 'des', 'ont', 'avec', 'pour', 'pas', 'plus',
    'cette', 'ces', 'leur', 'leurs', 'nous', 'vous', 'ils', 'elles',
}


# ── Individual checks ─────────────────────────────────────────────────────────

def check_tone(text, expected_sentiment, lang='en'):
    """
    Use the sentiment worker to verify the article sentiment matches expected_sentiment.
    Routes to FinBERT (English) or DistilCamemBERT (French) based on lang.
    Returns (tone_ok, confidence, model_label).
    Falls back gracefully if the worker is unavailable.
    """
    if not _get_finbert():
        return True, 0.0, 'unavailable'

    try:
        request = json.dumps({"text": text[:1024], "lang": lang}) + "\n"
        _worker_proc.stdin.write(request)
        _worker_proc.stdin.flush()
        response = _worker_proc.stdout.readline()
        result = json.loads(response)
        label = result['label'].lower()
        score = round(result['score'], 4)
        return label == expected_sentiment, score, label
    except Exception as e:
        print(f"[VERIFY] Sentiment inference error: {e}")
        return True, 0.0, 'error'


def check_company(text, company_name):
    """
    Check that the company name appears in the article.
    Strips ticker suffixes like '(MC)' before searching.
    """
    plain_name = re.split(r'\s*\(', company_name)[0].strip().lower()
    return plain_name in text.lower()


def check_curve_fit(text, curve_profile):
    """
    Compute a weighted vocabulary score for the given curve_profile.
    Returns (score, curve_ok).
    """
    vocab = CURVE_VOCABULARY.get(curve_profile, {})
    if not vocab:
        return 0, True  # unknown profile — skip check

    text_lower = text.lower()
    score = sum(weight for word, weight in vocab.items() if word in text_lower)
    return score, score >= CURVE_PASS_THRESHOLD


def check_language(text, expected_lang):
    """
    Detect language via stopword frequency and compare to expected_lang.
    Returns True if the detected language matches expected.
    """
    words = set(text.lower().split())
    en_count = len(words & _EN_STOPWORDS)
    fr_count = len(words & _FR_STOPWORDS)
    detected = 'en' if en_count >= fr_count else 'fr'
    return detected == expected_lang


# ── Master verifier ───────────────────────────────────────────────────────────

def verify_article(title, content, sentiment, company_name, curve_profile, lang):
    """
    Run all four checks on a generated article and return a result dict.

    Grading:
        A — all 4 checks pass, FinBERT confidence >= 0.75
        B — all 4 checks pass, FinBERT confidence >= 0.60
        C — 3 checks pass
        F — fewer than 3 checks pass, or tone/company fail

    Articles graded C or F are flagged and trigger a one-time retry in the
    generation pipeline.
    """
    full_text = title + ' ' + content

    tone_ok, tone_confidence, finbert_label = check_tone(full_text, sentiment, lang)
    company_mentioned                        = check_company(full_text, company_name)
    curve_score, curve_ok                   = check_curve_fit(full_text, curve_profile)
    language_ok                             = check_language(full_text, lang)

    checks_passed = sum([tone_ok, company_mentioned, curve_ok, language_ok])
    finbert_available = finbert_label not in ('unavailable', 'error')

    # DistilCamemBERT (French, 5 classes) produces lower per-class confidence
    # than FinBERT (English, 3 classes) — use lower thresholds for French.
    thresh_a = 0.40 if lang == 'fr' else 0.75
    thresh_b = 0.30 if lang == 'fr' else 0.60

    if finbert_available:
        if checks_passed == 4 and tone_confidence >= thresh_a:
            grade = 'A'
        elif checks_passed == 4 and tone_confidence >= thresh_b:
            grade = 'B'
        elif checks_passed >= 3:
            grade = 'C'
        else:
            grade = 'F'
    else:
        # FinBERT unavailable — grade on the three remaining checks only
        other_checks = sum([company_mentioned, curve_ok, language_ok])
        if other_checks == 3:
            grade = 'B'
        elif other_checks == 2:
            grade = 'C'
        else:
            grade = 'F'

    passed = grade in ('A', 'B')

    return {
        'tone_ok':           tone_ok,
        'tone_confidence':   tone_confidence,
        'finbert_label':     finbert_label,
        'company_mentioned': company_mentioned,
        'curve_score':       curve_score,
        'curve_ok':          curve_ok,
        'language_ok':       language_ok,
        'grade':             grade,
        'passed':            passed,
        'flagged':           not passed,
    }
