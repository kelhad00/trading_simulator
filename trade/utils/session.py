import io
import json
import os
import zipfile
from datetime import datetime


def build_session_zip(companies, initial_cashflow, max_requests, update_time, data_path, simulation_duration=None, news_font_size=None, color_scheme=None, notif_enabled=None, color_enabled=None, steps_per_candle=None, initial_bars=None, reminders_enabled=None, news_tags_enabled=None, leaderboard_enabled=None, commission_fee=None,
                      discrete_enabled=None, discrete_checkpoints=None):
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
                "color-enabled": color_enabled if color_enabled is not None else True,
                "steps-per-candle": steps_per_candle if steps_per_candle is not None else dlt.steps_per_candle,
                "initial-bars": initial_bars if initial_bars is not None else dlt.initial_reveal_bars,
                "reminders-enabled": reminders_enabled if reminders_enabled is not None else True,
                "news-tags-enabled": news_tags_enabled if news_tags_enabled is not None else True,
                "leaderboard-enabled": bool(leaderboard_enabled),
                "commission-fee": commission_fee if commission_fee is not None else dlt.commission_fee,
                "discrete-enabled": bool(discrete_enabled),
                "discrete-checkpoints": discrete_checkpoints or dlt.discrete_checkpoints,
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
        "color-enabled": stores.get("color-enabled", False),
        # Sessions saved before moving candles existed play as before (1 step = finished candles)
        "steps-per-candle": stores.get("steps-per-candle", 1),
        # Sessions saved before this setting existed start as before
        "initial-bars": stores.get("initial-bars", dlt.initial_reveal_bars),
        # Sessions saved before this switch existed: reminders on, as before
        "reminders-enabled": stores.get("reminders-enabled", True),
        # Sessions saved before this switch existed: news tags shown, as before
        "news-tags-enabled": stores.get("news-tags-enabled", True),
        # Sessions saved before the leaderboard existed: no leaderboard, as before
        "leaderboard-enabled": stores.get("leaderboard-enabled", False),
        # Sessions saved before fees existed: no fee, as before
        "commission-fee": stores.get("commission-fee", 0),
        # Sessions saved before discrete mode existed: running clock, as before
        "discrete-enabled": stores.get("discrete-enabled", False),
        "discrete-checkpoints": stores.get("discrete-checkpoints", dlt.discrete_checkpoints),
    }
