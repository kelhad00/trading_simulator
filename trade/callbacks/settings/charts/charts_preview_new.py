import json
import os
import warnings
from random import randint
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import callback, Input, Output, State, html, no_update, dcc
import dash_mantine_components as dmc
from plotly.graph_objs.layout.newshape import label

from trade.callbacks.settings.charts.modal import generate_new_charts
from trade.callbacks.settings.charts.patterns_generator import insert_bullish_engulfing, insert_bearish_engulfing, \
    insert_hammer, insert_shooting_star, insert_double_top, insert_head_and_shoulders, insert_double_bottom, \
    insert_inverse_head_and_shoulders
from trade.defaults import defaults as dlt
from trade.utils.graph.candlestick_charts import PLOTLY_CONFIG
import trade.callbacks.settings.charts.timeline_manager
import trade.callbacks.settings.charts.patterns_generator
import trade.callbacks.settings.charts.export_charts_to_csv
import trade.callbacks.settings.charts.delete_revenues
import trade.callbacks.settings.charts.pattern_manager
import trade.callbacks.settings.charts.modal
import trade.callbacks.settings.charts.update_graph
import trade.callbacks.settings.charts.company_table
import trade.callbacks.settings.charts.company_selection
import trade.callbacks.settings.charts.company_config


warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

bull_pattern = [
    "bullish_engulfing",
    "shooting_star",
    "double_bottom",
    "inverse_head_and_shoulders"
]
bear_pattern = [
    "bearish_engulfing",
    "hammer",
    "double_top",
    "head_and_shoulders"
]


# --- Logging utils ---
VERBOSE_LOGS = False

def _debug(msg: str):
    if VERBOSE_LOGS:
        print(msg)

def _progress_bar(done: int, total: int, width: int = 10) -> str:
    if total <= 0:
        return "[----------]"
    done = max(0, min(done, total))
    percent = int((done / total) * 100)
    filled = min(width, max(0, percent // (100 // width if width < 100 else 1)))
    bar = "[" + "=" * filled + f"{percent}%" + "-" * (width - filled) + "]"
    return bar

# callbacks.py
@callback(
    Output("chart_new", "children"),
    Output("new-graph-df", "data"),
    Input("refresh-button", "n_clicks"),
    State('size-store', "data"),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('granularity-select', 'value'),
    State("new-graph-df", "data"),
    State('special-pattern-config', 'data'),
    State('company-configs', 'data'),
    prevent_initial_call=True
)
def graph_preview_new(n_click, size_data, start_date, end_date, granularity, current_df, data_pattern, company_configs):
    """Generate preview graphs and export-ready data for configured companies.

    Args:
        n_click (int): Clicks on refresh button.
        size_data (dict): Timeline segments configuration with sizes and labels.
        start_date (str): Start date for generated data.
        end_date (str): End date for generated data.
        granularity (str): Pandas frequency string.
        current_df (dict|None): Existing data (unused; placeholder for future diffing).
        data_pattern (dict): Special patterns configuration per segment index.
        company_configs (dict): Per-company timeline and pattern configuration.

    Returns:
        tuple: (preview container children, simplified data dict for export)
    """
    # Loading placeholder while generating (use dcc.Loading for compatibility)
    loading = dcc.Loading(
        children=html.Div(style={"height": "300px"}),
        type="default",
        fullscreen=False
    )

    if size_data:
        for item in size_data:
            item_label = size_data[item]["label"]
            if size_data[item].get("pattern_type") is None:
                item_label = re.sub(r"\s*\(\d+(\.\d+)?%\)\s*$", "", item_label)
                if item_label == "Tête et épaules":
                    new_label = "head_and_shoulders"
                elif item_label == "Double sommet":
                    new_label = "double_top"
                elif item_label == "Double creux":
                    new_label = "double_bottom"
                elif item_label == "Tête et épaules inversés":
                    new_label = "inverse_head_and_shoulders"
                elif item_label == "Head and Shoulders":
                    new_label = "head_and_shoulders"
                elif item_label == "Double Top":
                    new_label = "double_top"
                elif item_label == "Double Bottom":
                    new_label = "double_bottom"
                elif item_label == "Inversed Head and Shoulders":
                    new_label = "inverse_head_and_shoulders"
            else:
                if "very" in item_label.lower() or "très" in item_label.lower():
                    new_label = "Very "
                elif "medium" in item_label.lower() or "moyen" in item_label.lower():
                    new_label = "Medium "
                else:
                    new_label = "Small "
                if "bear" in item_label.lower():
                    new_label += "Bear"
                else:
                    new_label += "Bull"
            size_data[item]["label"] = new_label

    # Only require date range and granularity; size_data can be empty when using saved configs
    if not all([start_date, end_date, granularity]):
        _debug("Invalid input")
        return loading, None

    dates = generate_date_range(start_date, end_date, granularity)
    # Use per-company configs; if none, skip
    if not isinstance(company_configs, dict) or len(company_configs) == 0:
        return dmc.Alert("Aucune configuration enregistrée.", color="gray"), None

    try:
        company_dfs = {}
        for company, cfg in company_configs.items():
            cfg_size = cfg.get("size_data", {})
            cfg_pattern = cfg.get("special_pattern_config", {})
            # Parse timeline sizes for this company
            trends, alphas, lengths, pattern_types = parse_size_data(cfg_size, len(dates))

            custom_pattern_list = []
            custom_pattern_count_list = []
            i = 0
            cfg_pattern = dict(cfg_pattern or {})
            for item in pattern_types:
                if item == "with":
                    if str(i) in cfg_pattern.keys():
                        custom_pattern_list.append(cfg_pattern[str(i)]["name"])
                        custom_pattern_count_list.append(cfg_pattern[str(i)]["count"])
                    else:
                        custom_pattern_list.append(bear_pattern if trends[i] == "bear" else bull_pattern)
                        custom_pattern_count_list.append([-1]*len(bear_pattern) if trends[i] == "bear" else [-1]*len(bull_pattern))
                else:
                    custom_pattern_list.append([])
                    custom_pattern_count_list.append([])
                i += 1

            # Build one company DataFrame
            company_df = pd.DataFrame(index=dates)
            date_cursor = 0
            for trend, alpha, length, pattern_type, custom_pattern_item, custom_pattern_count in zip(trends, alphas, lengths, pattern_types, custom_pattern_list, custom_pattern_count_list):
                trend_dates = dates[date_cursor:date_cursor + length]
                if pattern_type == "without":
                    handle_pattern_without(alpha, company, company_df, date_cursor, length, trend, trend_dates)
                elif pattern_type == "with":
                    handle_pattern_with(alpha, company, company_df, date_cursor, dates, length, trend, custom_pattern_item, custom_pattern_count)
                elif pattern_type is None:
                    handle_pattern_none(company_df, date_cursor, dates, length, trend)
                date_cursor += length

            company_df = finalize_company_df(company_df)
            compute_indicators(company_df)
            company_dfs[company] = ensure_column_order(company_df)

        if len(company_dfs) == 0:
            return loading, None

        df_global, data_dict = package_dataframe_for_export(company_dfs)

        children = build_preview_graphs(company_dfs)
        if not children:
            return loading, None

        return html.Div(children, style={"overflowY": "auto", "maxHeight": "80vh"}), data_dict
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        _debug(f"[ERROR] {e}")
        return loading, None


def handle_pattern_none(company_df, date_cursor, dates, length, trend):
    """Insert a configured complex pattern over a segment without extra patterns.

    Ensures continuity with previous values and sanitizes OHLC.
    """
    pattern_name = trend
    # Charger les paramètres du pattern depuis le JSON
    params = {}
    try:
        file_path = os.path.join(dlt.data_path, "pattern_configs.json")
        with open(file_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
        if pattern_name in configs:
            params = configs[pattern_name]
    except Exception as e:
        _debug(f"Erreur lors du chargement des paramètres du pattern {pattern_name} : {e}")
    # Générer les listes OHLC en continuant la série précédente
    n = length
    trend_dates = dates[date_cursor:date_cursor + length]  # <-- Correction ici
    # Déterminer la valeur de départ :
    if date_cursor == 0:
        start_value = randint(100, 1000)
        opens = [start_value] * n
        highs = [start_value] * n
        lows = [start_value] * n
        closes = [start_value] * n
    else:
        # On prend la dernière valeur de close déjà générée
        prev_close = company_df['Close'].iloc[date_cursor - 1]
        prev_open = company_df['Open'].iloc[date_cursor - 1]
        prev_high = company_df['High'].iloc[date_cursor - 1]
        prev_low = company_df['Low'].iloc[date_cursor - 1]
        if pd.isna(prev_close):
            # fallback si la valeur précédente n'est pas définie
            start_value = randint(100, 1000)
            opens = [start_value] * n
            highs = [start_value] * n
            lows = [start_value] * n
            closes = [start_value] * n
        else:
            opens = [prev_open] * n
            highs = [prev_high] * n
            lows = [prev_low] * n
            closes = [prev_close] * n
    params["duree"] = length
    # Appeler la bonne fonction d'insertion
    try:
        if pattern_name == "double_top":
            insert_double_top(opens, highs, lows, closes, 0, **params)
        elif pattern_name == "head_and_shoulders":
            insert_head_and_shoulders(opens, highs, lows, closes, 0, **params)
        elif pattern_name == "double_bottom":
            insert_double_bottom(opens, highs, lows, closes, 0, **params)
        elif pattern_name == "inverse_head_and_shoulders":
            insert_inverse_head_and_shoulders(opens, highs, lows, closes, 0, **params)
    except Exception as e:
        _debug(f"Erreur lors de l'insertion du pattern {pattern_name} : {e}")
    # Créer le DataFrame pour ce pattern
    df_trend = pd.DataFrame({
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": closes,
        "adjclose": closes,
        "Volume": [1000] * n
    }, index=trend_dates)
    # Sanitize + petite variation pour éviter un plateau initial
    try:
        sanitize_ohlc(df_trend)
        if len(df_trend) > 1:
            df_trend.loc[df_trend.index[1], 'Close'] = max(0.01, df_trend['Close'].iloc[1] * (1 + np.random.uniform(-0.001, 0.001)))
            df_trend.loc[df_trend.index[1], 'Open'] = max(0.01, df_trend['Open'].iloc[1] * (1 + np.random.uniform(-0.001, 0.001)))
            add_small_wicks(df_trend)
            sanitize_ohlc(df_trend)
    except Exception:
        pass
    # Remplir la tranche dans le DataFrame global de la société
    for col in df_trend.columns:
        company_df.loc[trend_dates, col] = df_trend[col].values
    date_cursor += length


def handle_pattern_with(alpha, company, company_df, date_cursor, dates, length, trend, custom_pattern_item: list ,custom_pattern_item_count):
    """Generate a segment possibly containing candlestick patterns.

    Tries to insert patterns respecting continuity; falls back to trend-based data.
    """
    # Charger la longueur du plus long pattern depuis pattern_configs.json
    import os, json
    file_path = os.path.join(dlt.data_path, "pattern_configs.json")
    with open(file_path, "r", encoding="utf-8") as f:
        configs = json.load(f)
    max_pattern_length = max([v.get("duree", 1) for v in configs.values()])
    min_block_size = max_pattern_length
    total_covered = 0
    last_close_block = None
    while total_covered < length:
        remaining = length - total_covered
        # Point de départ réel du sous-bloc dans la fenêtre globale de ce segment
        start_index = date_cursor + total_covered
        trend_dates_i = dates[start_index:start_index + remaining]
        if len(trend_dates_i) == 0:
            break
        # 50% de chance de mettre un pattern à la place du trend classique
        use_pattern = np.random.rand() < 0.5 and custom_pattern_item
        if use_pattern:
            # Choix du pattern et récupération de sa durée
            import time
            timeout = 1.0  # secondes
            pattern_ok = False
            pattern_attempt = 0
            start_time = time.time()
            while not pattern_ok and (time.time() - start_time < timeout):
                if not custom_pattern_item:
                    break
                pattern_name = np.random.choice(custom_pattern_item)
                try:
                    idx_choice = custom_pattern_item.index(pattern_name)
                except ValueError:
                    # Liste désynchronisée, on abandonne l'utilisation du pattern
                    use_pattern = False
                    break
                # Décrémenter le compteur associé
                if idx_choice < len(custom_pattern_item_count):
                    custom_pattern_item_count[idx_choice] = max(-1, custom_pattern_item_count[idx_choice] - 1)
                    if custom_pattern_item_count[idx_choice] <= 0:
                        # Retirer le pattern et son compteur pour garder les listes alignées
                        custom_pattern_item.pop(idx_choice)
                        custom_pattern_item_count.pop(idx_choice)
                else:
                    # Sécurité si désalignement
                    custom_pattern_item.pop(idx_choice)
                if pattern_name is not None:
                    # Charger les paramètres du pattern depuis le JSON
                    params = {}
                    try:
                        file_path = os.path.join(dlt.data_path, "pattern_configs.json")
                        with open(file_path, "r", encoding="utf-8") as f:
                            configs = json.load(f)
                        if pattern_name in configs:
                            params = configs[pattern_name]
                    except Exception as e:
                        _debug(f"Erreur lors du chargement des paramètres du pattern {pattern_name} : {e}")
                    # Déterminer la durée réelle du pattern
                    pattern_len = get_pattern_length(pattern_name)
                    n = min(pattern_len, remaining)  # ne pas dépasser le bloc restant
                    last_close = get_last_close(company_df, date_cursor)
                    if last_close is None:
                        start_value = randint(100, 1000)
                    else:
                        start_value = last_close
                    _debug(
                        f"[PATTERN] start_value for {company} at {date_cursor}: {start_value} (pattern: {pattern_name}) [essai {pattern_attempt+1}]")
                    opens = [start_value] * n
                    highs = [start_value] * n
                    lows = [start_value] * n
                    closes = [start_value] * n
                    # Vérifier que la fonction d'insertion modifie bien les listes passées !
                    try:
                        if pattern_name == "bullish_engulfing":
                            insert_bullish_engulfing(opens, highs, lows, closes, 0, **params)
                        elif pattern_name == "bearish_engulfing":
                            insert_bearish_engulfing(opens, highs, lows, closes, 0, **params)
                        elif pattern_name == "hammer":
                            insert_hammer(opens, highs, lows, closes, 0, **params)
                        elif pattern_name == "shooting_star":
                            insert_shooting_star(opens, highs, lows, closes, 0, **params)
                        elif pattern_name == "double_top":
                            insert_double_top(opens, highs, lows, closes, 0, **params)
                        elif pattern_name == "head_and_shoulders":
                            insert_head_and_shoulders(opens, highs, lows, closes, 0, **params)
                        elif pattern_name == "double_bottom":
                            insert_double_bottom(opens, highs, lows, closes, 0, **params)
                        elif pattern_name == "inverse_head_and_shoulders":
                            insert_inverse_head_and_shoulders(opens, highs, lows, closes, 0, **params)
                    except Exception as e:
                        _debug(f"Erreur lors de l'insertion du pattern {pattern_name} : {e}")
                    # --- Complétion si le pattern est plus court que la sous-tendance ---
                    pattern_len = len(opens)
                    if pattern_len < n:
                        last_open = opens[-1]
                        last_high = highs[-1]
                        last_low = lows[-1]
                        last_close = closes[-1]
                        opens += [last_open] * (n - pattern_len)
                        highs += [last_high] * (n - pattern_len)
                        lows += [last_low] * (n - pattern_len)
                        closes += [last_close] * (n - pattern_len)
                    # --- Continuité stricte avec le bloc précédent ---
                    if last_close_block is not None:
                        opens[0] = last_close_block
                        highs[0] = max(highs[0], last_close_block)
                        lows[0] = min(lows[0], last_close_block)
                        closes[0] = last_close_block
                    # --- PATCH DE SECURITE CONTINUITE & VALEURS ABERRANTES (STRICT) ---
                    opens[0] = start_value
                    closes[0] = start_value
                    highs[0] = max(highs[0], start_value)
                    lows[0] = min(lows[0], start_value)
                    # Sanitize all OHLC values to ensure numeric and reasonable bounds
                    for j in range(len(closes)):
                        for arr, name in zip([opens, highs, lows, closes], ["open", "high", "low", "close"]):
                            val = arr[j]
                            try:
                                v = float(val)
                            except (TypeError, ValueError):
                                _debug(f"[WARNING] Valeur non numérique dans pattern {pattern_name} ({name}) : {val} -> {start_value}")
                                arr[j] = float(start_value)
                                continue
                            # Replace zeros/negatives and extreme deviations
                            if v <= 0 or abs(v - start_value) > 10 * max(1, abs(start_value)):
                                _debug(f"[WARNING] Correction valeur aberrante dans pattern {pattern_name} ({name}) : {v} -> {start_value}")
                                arr[j] = float(start_value)
                            else:
                                arr[j] = v
                    # Compute max deviation safely
                    try:
                        safe_arrays = [np.array(opens, dtype=float), np.array(highs, dtype=float), np.array(lows, dtype=float), np.array(closes, dtype=float)]
                        max_dev = max([float(np.max(np.abs(arr - float(start_value)))) if arr.size > 0 else 0.0 for arr in safe_arrays])
                    except Exception:
                        max_dev = 0.0
                    if max_dev <= 2 * max(1, abs(start_value)):
                        pattern_ok = True
                        break  # On garde ce pattern
                    else:
                        _debug(
                            f"[SKIP PATTERN STRICT] Pattern {pattern_name} trop éloigné du start_value (max_dev={max_dev}), nouvel essai...")
                pattern_attempt += 1
            if not pattern_ok:
                _debug(f"[SKIP PATTERN ULTRA-STRICT] Aucun pattern valide trouvé après {pattern_attempt} essais et 1 seconde, génération d'un trend classique à la place.")
                use_pattern = False  # fallback sur trend classique
        if not use_pattern:
            n = min(min_block_size, remaining)
            last_close = last_close_block if last_close_block is not None else get_last_close(company_df, start_index)
            if last_close is None:
                start_value = randint(100, 1000)
            else:
                start_value = last_close
            _debug(f"[TREND] start_value for {company} at {date_cursor}: {start_value}")
            company_children, company_dataframes = generate_new_charts(
                alpha=alpha,
                length=n,
                start_value=start_value,
                radio_trends=[trend],
                companies=[company]
            )
            if company_dataframes and company_dataframes != no_update:
                df_trend = pd.DataFrame(company_dataframes[0])
                df_trend.index = trend_dates_i[:n]
                # Sanitize OHLC before merging
                try:
                    sanitize_ohlc(df_trend)
                except Exception:
                    pass
                # --- Continuité stricte avec le bloc précédent ---
                if last_close_block is not None:
                    # Rebase entier du sous-bloc pour matcher last_close_block
                    rebase_chunk_to_last_close(df_trend, last_close_block)
                else:
                    # Si aucun bloc précédent, on rebased sur start_value pour éliminer l'escalier initial
                    rebase_chunk_to_last_close(df_trend, start_value)
                # Empêcher long plateau: variation minime dès le 2e point et wicks
                if len(df_trend) > 1:
                    df_trend.loc[df_trend.index[1], 'Close'] = max(0.01, df_trend['Close'].iloc[0] * (1 + np.random.uniform(0.0005, 0.002)))
                    df_trend.loc[df_trend.index[1], 'Open'] = max(0.01, df_trend['Open'].iloc[0] * (1 + np.random.uniform(-0.0005, 0.002)))
                    try:
                        add_small_wicks(df_trend)
                        sanitize_ohlc(df_trend)
                    except Exception:
                        pass
                last_close_block = df_trend['Close'].iloc[-1]
                # Micro variation to avoid long plateaus
                try:
                    add_micro_variation(df_trend)
                except Exception:
                    pass
                for col in df_trend.columns:
                    company_df.loc[trend_dates_i[:n], col] = df_trend[col].values
                _debug(f"[TREND] last close for {company} at {date_cursor + n - 1}: {df_trend['Close'].iloc[-1]}")
            else:
                _debug("[TREND] Aucune donnée retournée par generate_new_charts, on saute ce sous-bloc")
            total_covered += n
            continue
        # Si pattern_ok, on continue la logique normale (création du DataFrame, etc.)
        # --- Retirer la première bougie du pattern, puis utiliser la longueur réelle restante ---
        if len(opens) > 1 and len(highs) > 1 and len(lows) > 1 and len(closes) > 1:
            opens = opens[1:]
            highs = highs[1:]
            lows = lows[1:]
            closes = closes[1:]
        # Longueur réellement utilisable pour ce sous-bloc
        used_len = min(len(opens), len(highs), len(lows), len(closes), len(trend_dates_i[:n]))
        min_len = used_len
        if min_len <= 0:
            # Pattern trop court après retrait de la 1ère bougie -> fallback trend sur un mini-bloc
            use_pattern = False
            continue
        if not (len(opens) == len(highs) == len(lows) == len(closes) == len(trend_dates_i[:n])):
            _debug(f"[ERREUR] Mismatch de longueur : opens={len(opens)}, highs={len(highs)}, lows={len(lows)}, closes={len(closes)}, dates={len(trend_dates_i[:n])}")
        opens = opens[:min_len]
        highs = highs[:min_len]
        lows = lows[:min_len]
        closes = closes[:min_len]
        trend_dates = trend_dates_i[:min_len]
        df_trend = pd.DataFrame({
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "adjclose": closes,
            "Volume": [1000] * min_len
        }, index=trend_dates)
        # Sanitize OHLC before merging
        try:
            sanitize_ohlc(df_trend)
        except Exception:
            pass
        if last_close_block is not None:
            rebase_chunk_to_last_close(df_trend, last_close_block)
        else:
            rebase_chunk_to_last_close(df_trend, opens[0] if len(opens) else df_trend['Close'].iloc[0])
        # Empêcher long plateau dès le 2e point + wicks
        if len(df_trend) > 1:
            df_trend.loc[df_trend.index[1], 'Close'] = max(0.01, df_trend['Close'].iloc[0] * (1 + np.random.uniform(0.0005, 0.002)))
            df_trend.loc[df_trend.index[1], 'Open'] = max(0.01, df_trend['Open'].iloc[0] * (1 + np.random.uniform(-0.0005, 0.002)))
            try:
                add_small_wicks(df_trend)
                sanitize_ohlc(df_trend)
            except Exception:
                pass
        last_close_block = df_trend['Close'].iloc[-1]
        try:
            add_micro_variation(df_trend)
        except Exception:
            pass
        for col in df_trend.columns:
            company_df.loc[trend_dates, col] = df_trend[col].values
        _debug(f"[PATTERN->TREND] last close for {company} at {date_cursor + min_len - 1}: {closes[-1]}")
        total_covered += min_len


def handle_pattern_without(alpha, company, company_df, date_cursor, length, trend, trend_dates):
    """Generate a pure trend segment without patterns, keeping OHLC continuity."""
    last_close = get_last_close(company_df, date_cursor)
    if last_close is None:
        start_value = randint(100, 1000)
    else:
        start_value = last_close
    _debug(f"[WITHOUT] start_value for {company} at {date_cursor}: {start_value}")
    # Générer les données pour cette tranche
    company_children, company_dataframes = generate_new_charts(
        alpha=alpha,
        length=len(trend_dates),
        start_value=start_value,
        radio_trends=[trend],
        companies=[company]
    )
    if company_dataframes and company_dataframes != no_update:
        df_trend = pd.DataFrame(company_dataframes[0])
        df_trend.index = trend_dates
        # --- PATCH CONTINUITE : forcer la première valeur à start_value ---
        # Rebase entier du chunk sur start_value pour éviter l'escalier
        try:
            rebase_chunk_to_last_close(df_trend, start_value)
        except Exception:
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df_trend.columns:
                    if abs(df_trend[col].iloc[0] - start_value) > 1e-6:
                        _debug(
                            f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                        df_trend.loc[df_trend.index[0], col] = start_value
        # Remplir la tranche dans le DataFrame global de la société
        try:
            sanitize_ohlc(df_trend)
            add_micro_variation(df_trend)
        except Exception:
            pass
        for col in df_trend.columns:
            company_df.loc[trend_dates, col] = df_trend[col].values
        # Log de la dernière valeur générée
        _debug(
            f"[WITHOUT] last close for {company} at {date_cursor + len(trend_dates) - 1}: {df_trend['Close'].iloc[-1]}")
    date_cursor += length


def get_pattern_length(label):
    """Return expected number of candles for a given pattern label."""
    file_path = os.path.join(dlt.data_path, "pattern_configs.json")
    pattern_key = label.lower().replace(" ", "_")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
        if pattern_key in configs and "duree" in configs[pattern_key]:
            return int(configs[pattern_key]["duree"])
    except Exception:
        pass
    # Fallback logique par défaut
    if pattern_key in ["bullish_engulfing", "bearish_engulfing"]:
        return 2
    elif pattern_key in ["hammer", "shooting_star"]:
        return 1
    # Ajoute d'autres patterns si besoin
    return 3  # valeur par défaut


def get_last_close(company_df, date_cursor):
    """Find the last non-NaN Close before the given index for continuity."""
    if date_cursor == 0:
        return None
    prev_closes = company_df['Close'].iloc[:date_cursor].dropna()
    if not prev_closes.empty:
        return prev_closes.iloc[-1]
    return None


def is_input_valid(size_data, start_date, end_date, granularity):
    """Check minimal validity of preview inputs."""
    return all([size_data, start_date, end_date, granularity])


def generate_date_range(start_date, end_date, granularity):
    """Generate a pandas.DatetimeIndex based on dates and frequency."""
    return pd.date_range(start=start_date, end=end_date, freq=granularity)


def parse_size_data(size_data, global_length):
    """Parse timeline blocks into trends, alphas, lengths and types lists."""
    alpha_map = {
        "Very Bull": 1000, "Medium Bull": 500, "Small Bull": 250,
        "Flat": 100,
        "Very Bear": 250, "Medium Bear": 500, "Small Bear": 1000
    }
    trends, alphas, lengths, pattern_types = [], [], [], []

    for item in size_data:
        item_data = size_data[item]
        if item_data["width"] == 0:
            continue
        label = item_data["label"]
        alpha = alpha_map.get(label, 100)
        trend = "bull" if "Bull" in label else "bear" if "Bear" in label else label
        pattern_type = item_data.get("pattern_type", "with")
        length = item_data["width"]
        trends.append(trend)
        alphas.append(alpha)
        lengths.append(length)
        pattern_types.append(pattern_type)

    lengths = resize_lengths_to_fit(lengths, global_length)
    return trends, alphas, lengths, pattern_types


def resize_lengths_to_fit(lengths, target):
    """Rescale block lengths so their sum equals target size."""
    total = sum(lengths)
    if total == 0:
        return [0] * len(lengths)
    resized = [int(l / total * target) for l in lengths]
    diff = target - sum(resized)
    resized[-1] += diff
    return resized


def generate_company_dataframes(dates, companies, trends, alphas, lengths, pattern_types, custom_pattern_list, custom_pattern_count_list):
    """Produce per-company OHLC DataFrames for preview/export based on configs."""
    company_dfs = {}
    total = len(companies)
    done = 0
    for company in companies:
        company_df = pd.DataFrame(index=dates)
        date_cursor = 0
        for trend, alpha, length, pattern_type, custom_pattern_item, custom_pattern_count in zip(trends, alphas, lengths, pattern_types, custom_pattern_list, custom_pattern_count_list):
            trend_dates = dates[date_cursor:date_cursor + length]
            if pattern_type == "without":
                handle_pattern_without(alpha, company, company_df, date_cursor, length, trend, trend_dates)
            elif pattern_type == "with":
                handle_pattern_with(alpha, company, company_df, date_cursor, dates, length, trend, custom_pattern_item, custom_pattern_count)
            elif pattern_type is None:
                handle_pattern_none(company_df, date_cursor, dates, length, trend)
            date_cursor += length

        # Finalize consistency
        company_df = finalize_company_df(company_df)
        compute_indicators(company_df)
        company_dfs[company] = ensure_column_order(company_df)
        done += 1
        bar = _progress_bar(done, total, width=10)
        print(f"{bar} {done}/{total} - {company} terminé")

    return company_dfs


def compute_indicators(df):
    """Compute common indicators (moving averages and RSI) on Close series."""
    if "Close" not in df.columns:
        return
    df['short_MA'] = df['Close'].rolling(window=20, min_periods=1).mean()
    df['long_MA'] = df['Close'].rolling(window=50, min_periods=1).mean()
    df['200_MA'] = df['Close'].rolling(window=200, min_periods=1).mean()

    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))


def ensure_column_order(df):
    """Ensure a stable column order with all expected fields present."""
    expected_cols = ['Open', 'High', 'Low', 'Close', 'adjclose', 'Volume', 'long_MA', 'short_MA', '200_MA', 'RSI']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = np.nan
    return df[expected_cols]


def sanitize_ohlc(df: pd.DataFrame) -> None:
    """Clean and normalize OHLC to maintain coherence.

    - Fill NaNs from close forward/backward
    - Ensure High >= max(Open, Close) and Low <= min(Open, Close)
    - Avoid fully-flat bars by adding a tiny wick
    - Enforce strictly positive prices
    """
    for col in ['Open', 'High', 'Low', 'Close']:
        if col not in df.columns:
            df[col] = np.nan
        # Coerce to numeric
        df[col] = pd.to_numeric(df[col], errors='coerce')

    base_series = df['Close'].ffill().bfill()
    base_series = base_series.fillna(100.0)
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = df[col].fillna(base_series)

    # Enforce OHLC bounds
    max_oc = np.maximum(df['Open'].values, df['Close'].values)
    min_oc = np.minimum(df['Open'].values, df['Close'].values)
    df['High'] = np.maximum(df['High'].values, max_oc)
    df['Low'] = np.minimum(df['Low'].values, min_oc)

    # Avoid fully flat candles
    same_all = (
        (df['Open'] == df['High']) &
        (df['High'] == df['Low']) &
        (df['Low'] == df['Close'])
    )
    if same_all.any():
        prices = df.loc[same_all, 'Close']
        tiny = np.maximum(0.001 * prices.abs(), 0.01)
        df.loc[same_all, 'High'] = prices + tiny
        df.loc[same_all, 'Low'] = np.maximum(prices - tiny, 0.01)

    # Strictly positive prices
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = df[col].clip(lower=0.01)


def add_micro_variation(df: pd.DataFrame, tol: float = 1e-9, eps_pct: float = 0.001) -> None:
    """Inject tiny variation when consecutive closes are strictly flat.

    eps_pct is relative to previous close (e.g. 0.001 = 0.1%). Keeps OHLC
    consistency after adjustment.
    """
    if 'Close' not in df.columns:
        return
    closes = df['Close'].values
    opens = df['Open'].values if 'Open' in df.columns else closes.copy()
    highs = df['High'].values if 'High' in df.columns else closes.copy()
    lows = df['Low'].values if 'Low' in df.columns else closes.copy()
    for i in range(1, len(closes)):
        if abs(closes[i] - closes[i-1]) <= tol:
            prev = closes[i-1]
            delta = prev * np.random.uniform(-eps_pct, eps_pct)
            closes[i] = max(0.01, prev + delta)
            # Adjust open toward close but not equal
            opens[i] = max(0.01, (opens[i] + closes[i]) / 2.0)
            # Ensure bounds
            highs[i] = max(highs[i], opens[i], closes[i])
            lows[i] = min(lows[i], opens[i], closes[i])
    df['Close'] = closes
    df['Open'] = opens
    df['High'] = highs
    df['Low'] = lows


def add_small_wicks(
    df: pd.DataFrame,
    wick_min: float = 0.0005,
    wick_max: float = 0.002,
    wick_cap: float = 0.02,
) -> None:
    """Ensure wicks exist but remain within reasonable bounds.

    - Adds a tiny random wick (between wick_min and wick_max)
    - Caps wick size to wick_cap relative to max(Open, Close) and min(Open, Close)
    """
    if not {'Open', 'High', 'Low', 'Close'}.issubset(df.columns):
        return
    o = df['Open'].values
    c = df['Close'].values
    base_high = np.maximum(o, c)
    base_low = np.minimum(o, c)
    up = np.random.uniform(wick_min, wick_max, size=len(df))
    down = np.random.uniform(wick_min, wick_max, size=len(df))
    proposed_high = np.maximum(df['High'].values, base_high * (1 + up))
    proposed_low = np.minimum(df['Low'].values, base_low * (1 - down))
    # Cap extremes
    cap_high = base_high * (1 + wick_cap)
    cap_low = base_low * (1 - wick_cap)
    df['High'] = np.minimum(proposed_high, cap_high)
    df['Low'] = np.maximum(proposed_low, cap_low)


def finalize_company_df(df: pd.DataFrame) -> pd.DataFrame:
    """Run final coherence fixes on a full company dataframe."""
    try:
        sanitize_ohlc(df)
        add_micro_variation(df, tol=1e-9, eps_pct=0.001)
        add_small_wicks(df)
        sanitize_ohlc(df)
    except Exception:
        pass
    return df


def rebase_chunk_to_last_close(df: pd.DataFrame, target_close: float) -> None:
    """Rescale OHLC chunk so first Close equals target_close.

    Preserves relative shape and removes junction jumps.
    """
    if df.empty or not {'Open','High','Low','Close'}.issubset(df.columns):
        return
    first_close = float(df['Close'].iloc[0]) if df['Close'].iloc[0] not in [None, np.nan] else target_close
    if first_close == 0:
        first_close = 1.0
    factor = target_close / first_close if first_close != 0 else 1.0
    for col in ['Open','High','Low','Close']:
        df[col] = pd.to_numeric(df[col], errors='coerce') * factor
    # align first open to target_close to remove tiny discrepancy
    df.loc[df.index[0], 'Open'] = target_close
    try:
        add_small_wicks(df)
        sanitize_ohlc(df)
    except Exception:
        pass


def package_dataframe_for_export(company_dfs):
    """Pack multi-company DataFrame and a simplified dict for serialization."""
    df_global = pd.concat(company_dfs.values(), axis=1, keys=company_dfs.keys(), names=['symbol'])
    data_dict = {
        'data': {
            f'{col[0]}|{col[1]}': [str(x) if isinstance(x, (pd.Timestamp, np.datetime64)) else x for x in
                                   df_global[col]]
            for col in df_global.columns
        },
        'column_names': [f'{col[0]}|{col[1]}' for col in df_global.columns],
        'index': [str(x) for x in df_global.index]
    }
    return df_global, data_dict


def build_preview_graphs(company_dfs):
    """Build Plotly preview graphs per company from generated DataFrames."""
    graphs = []
    for company, df in company_dfs.items():
        # Sanitize to avoid incoherent flat steps and NaNs
        try:
            sanitize_ohlc(df)
        except Exception:
            pass
        fig = go.Figure()
        try:
            fig.add_trace(go.Candlestick(
                x=[str(x) for x in df.index],
                open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                name=company
            ))
            fig.update_layout(title=f"Prévisualisation {company}", xaxis_title="Date", yaxis_title="Cours")
        except Exception:
            fig.add_trace(go.Scatter(x=[], y=[], name="Erreur"))
            fig.update_layout(title=f"Erreur avec {company}")
        graphs.append(dcc.Graph(figure=fig, config=PLOTLY_CONFIG))
    return graphs
