from uuid import uuid4

import csv
import io
import json
import threading

import pandas as pd
from datetime import datetime
import os
from dash import page_registry

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.logs import get_logger

logger = get_logger("export")


def format_portfolio_dataframe(df, name):
    try:
        df = pd.DataFrame.from_dict(df, orient='index').T
        columns = dict(zip(df.columns, [col + name for col in df.columns]))
        df.rename(columns=columns, inplace=True)
        return df
    except:
        return pd.DataFrame()

def format_requests_dataframe(request_list, max_requests):
    try:
        new_columns_data = {}
        df = pd.DataFrame(request_list, columns=['action', 'shares', 'company', 'price']).T
        for i in range(0, max_requests):  # Parcourir les 10 actions (de 1 à 10)
            action_col_name = f"request-{i+1}"
            try:
                action_data = df[i]  # Extraire les données pour l'action i
                new_columns_data[action_col_name] = f"{action_data['action']} {action_data['price']} {action_data['shares']} {action_data['company']}"
            except:
                new_columns_data[action_col_name] = None

        return pd.DataFrame.from_dict(new_columns_data, orient="index").T
    except:
        return pd.DataFrame()



def format_charts_type(chart_type):
    lang = page_registry.get('lang', 'fr')
    if chart_type == tls[lang]['tab-market']:
        return "market"
    else:
        return "revenue"


def format_deleted_requests(deleted_request):
    if deleted_request is None:
        deleted_request = []
    else:
        deleted_request = list(deleted_request)
    return deleted_request


def export_data(
        timestamp,
        request_list,
        cashflow,
        shares,
        totals,
        company_id,
        news_title,
        graph_type,  # used to know which type of charts is displayed
        form_type,  # used to know if user is going to buy or sell
        deleted_request=None,
        trigger=None,
        max_requests=dlt.max_requests
):
    """ Periodically save state of the trade into csv
    """

    deleted_request = format_deleted_requests(deleted_request)
    charts = format_charts_type(graph_type)
    requests = format_requests_dataframe(request_list, max_requests)
    shares = format_portfolio_dataframe(shares, "-shares")
    totals = format_portfolio_dataframe(totals, "-totals")

    # generate an uuid
    uuid = str(uuid4())

    df = pd.DataFrame({
        "uuid": [uuid],
        "market-timestamp": [timestamp],
        "host-timestamp": [datetime.now().timestamp()],
        "cashflow": [cashflow],
        "selected-company": [company_id],
        "form-action": [form_type],
        "chart-type": [charts],
        "is_news_description_displayed" : [False if news_title is None else True],
        "news_title" : [news_title],
    })

    portfolio_df = pd.DataFrame({"uuid": [uuid]})
    portfolio_df = portfolio_df.merge(shares, how='left', left_index=True, right_index=True)
    portfolio_df = portfolio_df.merge(totals, how='left', left_index=True, right_index=True)

    request_df = pd.DataFrame({"uuid": [uuid], "deleted-request": [deleted_request]})
    request_df = request_df.merge(requests, how='left', left_index=True, right_index=True)

    # Save the header only once and append the rest
    file_path = os.path.join(dlt.data_path, 'export', 'interface-logs.csv')
    portfolio_path = os.path.join(dlt.data_path, 'export', 'portfolio-logs.csv')
    request_path = os.path.join(dlt.data_path, 'export', 'request-logs.csv')

    save_df(df, file_path)
    save_df(portfolio_df, portfolio_path)
    save_df(request_df, request_path)


def log_session_event(event, timestamp=None, cashflow=None, company_id=None):
    """ Log a session lifecycle event (start/pause/resume/finish) into interface-logs.csv """
    uuid = str(uuid4())

    df = pd.DataFrame({
        "uuid": [uuid],
        "market-timestamp": [timestamp],
        "host-timestamp": [datetime.now().timestamp()],
        "cashflow": [cashflow],
        "selected-company": [company_id],
        "form-action": [event],
        "chart-type": [None],
        "is_news_description_displayed": [False],
        "news_title": [None],
    })

    file_path = os.path.join(dlt.data_path, 'export', 'interface-logs.csv')
    save_df(df, file_path)


# Several parts of the app write logs at the same moment (threaded server): one
# writer at a time, otherwise their lines get mixed inside the file.
_LOG_LOCK = threading.Lock()

# Bump only when the meaning of existing log columns changes (not for new columns:
# those are added automatically by save_df).
LOG_FORMAT_VERSION = 2


def _as_text(df):
    """The rows exactly as to_csv would write them, as text (so merging keeps values unchanged)."""
    return pd.read_csv(io.StringIO(df.to_csv(index=False)), dtype=str, keep_default_na=False)


def _read_header(file_path):
    with open(file_path, newline="", encoding="utf-8") as f:
        return next(csv.reader(f), [])


def _next_free_part(file_path):
    base, ext = os.path.splitext(file_path)
    n = 2
    while os.path.exists(f"{base}-{n}{ext}"):
        n += 1
    return f"{base}-{n}{ext}"


def save_df(df, file_path):
    """Add rows to a log CSV, keeping every value under its own column name.

    - Same columns as the file: the rows are appended (the usual case).
    - Different columns (companies or settings changed, or a new column was
      added in the code): the file is rewritten with all columns, old rows get
      empty cells for the new ones, so nothing ends up under the wrong header.
    - A file already damaged by older versions can't be merged safely: it is
      left untouched and the rows go to a new part (e.g. portfolio-logs-2.csv).
    """
    with _LOG_LOCK:
        if not os.path.isfile(file_path):
            df.to_csv(file_path, index=False)
            return

        if _read_header(file_path) == list(df.columns):
            df.to_csv(file_path, mode='a', index=False, header=False)
            return

        try:
            old = pd.read_csv(file_path, dtype=str, keep_default_na=False)
        except (pd.errors.ParserError, UnicodeDecodeError):
            old = None

        if old is None:
            part = _next_free_part(file_path)
            logger.warning("%s has damaged rows: new log rows go to %s", os.path.basename(file_path),
                           os.path.basename(part))
            df.to_csv(part, index=False)
            return

        new = _as_text(df)
        columns = list(old.columns) + [c for c in new.columns if c not in old.columns]
        merged = pd.concat([old, new], ignore_index=True).reindex(columns=columns).fillna("")
        merged.to_csv(file_path, index=False)
        logger.info("%s: columns changed, file rewritten with all columns aligned by name",
                    os.path.basename(file_path))


def _app_version():
    """Short id of the TradeSim code version (git commit), read from the .git folder."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    git = os.path.join(root, ".git")
    try:
        head = open(os.path.join(git, "HEAD"), encoding="utf-8").read().strip()
        if not head.startswith("ref: "):
            return head[:7]
        ref = head[5:]
        ref_file = os.path.join(git, *ref.split("/"))
        if os.path.isfile(ref_file):
            return open(ref_file, encoding="utf-8").read().strip()[:7]
        for line in open(os.path.join(git, "packed-refs"), encoding="utf-8"):
            if line.strip().endswith(" " + ref):
                return line.split()[0][:7]
    except OSError:
        pass
    return "unknown"


def write_log_info(settings):
    """Record, next to the logs, which code version and settings a session ran with.

    Written automatically at each session start into export/log-info.json (one
    entry per session start), and archived with the logs on reset.
    """
    path = os.path.join(dlt.data_path, 'export', 'log-info.json')
    with _LOG_LOCK:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, encoding="utf-8") as f:
                info = json.load(f)
        except (OSError, ValueError):
            info = {}
        info["log_format_version"] = LOG_FORMAT_VERSION
        info.setdefault("sessions", []).append({
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "tradesim_version": _app_version(),
            "settings": settings,
        })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
