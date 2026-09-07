import io
import json
import os
import zipfile
from datetime import datetime


def build_session_zip(companies, initial_cashflow, max_requests, update_time, data_path, simulation_duration=None, news_font_size=None, color_scheme=None, notif_enabled=None):
    """Package stores + CSV files into an in-memory ZIP and return the bytes."""
    from trade.defaults import defaults as dlt
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        payload = {
            "version": 1,
            "exported_at": datetime.utcnow().isoformat(),
            "stores": {
                "companies": companies,
                "initial-cashflow": initial_cashflow,
                "max-requests": max_requests,
                "update-time": update_time,
                "simulation-duration": simulation_duration if simulation_duration is not None else dlt.simulation_duration,
                "news-font-size": news_font_size if news_font_size is not None else dlt.news_font_size,
                "color-scheme": color_scheme or "light",
                "notif-enabled": notif_enabled if notif_enabled is not None else True,
            }
        }
        zf.writestr("session.json", json.dumps(payload, ensure_ascii=False, indent=2))

        for filename in ("generated_data.csv", "news.csv", "revenues.csv"):
            path = os.path.join(data_path, filename)
            if os.path.exists(path):
                zf.write(path, filename)

    return buf.getvalue()


def extract_session_zip(zip_bytes, data_path):
    """Extract a session ZIP, write CSVs to data_path, return store values dict."""
    buf = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(buf, "r") as zf:
        names = zf.namelist()

        if "session.json" not in names:
            raise ValueError("Invalid session file: missing session.json")

        payload = json.loads(zf.read("session.json"))
        if payload.get("version") != 1:
            raise ValueError("Unsupported session version")

        stores = payload["stores"]

        for filename in ("generated_data.csv", "news.csv", "revenues.csv"):
            if filename in names:
                dest = os.path.join(data_path, filename)
                with open(dest, "wb") as f:
                    f.write(zf.read(filename))

    from trade.defaults import defaults as dlt
    return {
        "companies": stores["companies"],
        "initial-cashflow": stores["initial-cashflow"],
        "max-requests": stores["max-requests"],
        "update-time": stores["update-time"],
        "simulation-duration": stores.get("simulation-duration", dlt.simulation_duration),
        "news-font-size": stores.get("news-font-size", dlt.news_font_size),
        "color-scheme": stores.get("color-scheme", "light"),
        "notif-enabled": stores.get("notif-enabled", True),
    }
