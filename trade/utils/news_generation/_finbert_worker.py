"""
Persistent sentiment worker process.
Reads one JSON line from stdin per request, writes one JSON line to stdout.
Prints READY once the model is loaded and ready to accept requests.

Request:  {"text": "...", "lang": "en"}   (lang is accepted but not needed — model is multilingual)
Response: {"label": "positive"|"negative"|"neutral", "score": 0.0}

Model:
  Kenpache/finbert-multilingual — single model handling EN and FR (and ZH, JA, DE, ES)
  Outputs 3 classes directly: negative / neutral / positive
  No label mapping needed.
"""
import sys
import os
import json

os.environ["TRANSFORMERS_VERBOSITY"] = "error"

from transformers import pipeline

sys.stderr.write("[VERIFY] Loading FinBERT-Multilingual — downloading if not cached, this may take a few minutes...\n")
sys.stderr.flush()

_model = pipeline(
    "text-classification",
    model="Kenpache/finbert-multilingual",
    truncation=True,
    max_length=512,
)

sys.stderr.write("[VERIFY] FinBERT-Multilingual loaded successfully.\n")
sys.stderr.flush()

sys.stdout.write("READY\n")
sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req   = json.loads(line)
        text  = req["text"]
        raw   = _model(text)[0]
        label = raw["label"].lower()
        score = raw["score"]
        sys.stdout.write(json.dumps({"label": label, "score": score}) + "\n")
        sys.stdout.flush()
    except Exception:
        sys.stdout.write(json.dumps({"label": "error", "score": 0.0}) + "\n")
        sys.stdout.flush()
