"""
Persistent sentiment worker process.
Reads one JSON line from stdin per request, writes one JSON line to stdout.
Prints READY once both models are loaded and ready to accept requests.

Request:  {"text": "...", "lang": "en"}   (lang defaults to "en")
Response: {"label": "positive"|"negative"|"neutral", "score": 0.0}

Models:
  lang=en -> ProsusAI/finbert                        (English financial sentiment)
  lang=fr -> cmarkea/distilcamembert-base-sentiment  (French sentiment)

DistilCamemBERT outputs 1-5 stars; mapped to pos/neg/neutral:
  1-2 stars -> negative  |  3 stars -> neutral  |  4-5 stars -> positive
"""
import sys
import os
import json

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from transformers import pipeline

_finbert = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert",
    truncation=True,
    max_length=512,
)

_camembert = pipeline(
    "sentiment-analysis",
    model="cmarkea/distilcamembert-base-sentiment",
    truncation=True,
    max_length=512,
)

_CAMEMBERT_MAP = {
    "1 star":  "negative",
    "2 stars": "negative",
    "3 stars": "neutral",
    "4 stars": "positive",
    "5 stars": "positive",
}

sys.stdout.write("READY\n")
sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req  = json.loads(line)
        lang = req.get("lang", "en")
        text = req["text"]

        if lang == "fr":
            raw   = _camembert(text)[0]
            label = _CAMEMBERT_MAP.get(raw["label"].lower(), "neutral")
            score = raw["score"]
        else:
            raw   = _finbert(text)[0]
            label = raw["label"].lower()
            score = raw["score"]

        sys.stdout.write(json.dumps({"label": label, "score": score}) + "\n")
        sys.stdout.flush()
    except Exception:
        sys.stdout.write(json.dumps({"label": "error", "score": 0.0}) + "\n")
        sys.stdout.flush()
