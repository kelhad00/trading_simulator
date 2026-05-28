"""
Persistent FinBERT worker process.
Reads one JSON line from stdin per request, writes one JSON line to stdout.
Prints READY once the model is loaded and ready to accept requests.
"""
import sys
import os
import json

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from transformers import pipeline

finbert = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert",
    truncation=True,
    max_length=512,
)

sys.stdout.write("READY\n")
sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
        result = finbert(req["text"])[0]
        sys.stdout.write(json.dumps({"label": result["label"], "score": result["score"]}) + "\n")
        sys.stdout.flush()
    except Exception:
        sys.stdout.write(json.dumps({"label": "error", "score": 0.0}) + "\n")
        sys.stdout.flush()
