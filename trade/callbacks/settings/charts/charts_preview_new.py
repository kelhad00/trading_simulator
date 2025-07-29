import json
import os
import warnings
from random import randint

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import callback, Input, Output, State, html, no_update, dcc

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
    prevent_initial_call=True
)
def graph_preview_new(n_click, size_data, start_date, end_date, granularity, current_df):
    if not is_input_valid(size_data, start_date, end_date, granularity):
        return html.Div(), None

    dates = generate_date_range(start_date, end_date, granularity)
    if len(dates) == 0:
        return html.Div(), None

    trends, alphas, lengths, pattern_types = parse_size_data(size_data, len(dates))

    companies = list(dlt.companies_list.keys())
    if not companies:
        return html.Div(), None

    try:
        company_dfs = generate_company_dataframes(dates, companies, trends, alphas, lengths, pattern_types)
        df_global, data_dict = package_dataframe_for_export(company_dfs)

        children = build_preview_graphs(company_dfs)
        if not children:
            return html.Div(), None

        return html.Div(children, style={"overflowY": "auto", "maxHeight": "80vh"}), data_dict
    except Exception as e:
        print(f"[ERROR] {e}")
        return html.Div(), None


def handle_pattern_none(company_df, date_cursor, dates, length, trend):
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
        print(f"Erreur lors du chargement des paramètres du pattern {pattern_name} : {e}")
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
        print(f"Erreur lors de l'insertion du pattern {pattern_name} : {e}")
    # Créer le DataFrame pour ce pattern
    df_trend = pd.DataFrame({
        "Open": opens,
        "High": highs,
        "Low": lows,
        "Close": closes,
        "adjclose": closes,
        "Volume": [1000] * n
    }, index=trend_dates)
    # Remplir la tranche dans le DataFrame global de la société
    for col in df_trend.columns:
        company_df.loc[trend_dates, col] = df_trend[col].values
    date_cursor += length


def handle_pattern_with(alpha, company, company_df, date_cursor, dates, length, trend):
    subtrend_nb = 10
    subtrend_lengths = [length // subtrend_nb] * subtrend_nb
    if sum(subtrend_lengths) != length:
        subtrend_lengths[-1] += length - sum(subtrend_lengths)
    for i in range(subtrend_nb):
        sub_len = subtrend_lengths[i]
        trend_dates_i = dates[date_cursor:date_cursor + sub_len]
        if len(trend_dates_i) == 0:
            continue
        # 50% de chance de mettre un pattern à la place du trend classique
        if np.random.rand() < 0.5:
            # Choix du pattern cohérent avec la tendance
            if trend == "bull":
                pattern_name = np.random.choice(bull_pattern)
            elif trend == "bear":
                pattern_name = np.random.choice(bear_pattern)
            else:
                pattern_name = None
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
                    print(f"Erreur lors du chargement des paramètres du pattern {pattern_name} : {e}")
                # Déterminer la durée réelle du pattern
                pattern_len = get_pattern_length(pattern_name)
                pattern_len = min(pattern_len, sub_len)  # ne pas dépasser la sous-tranche
                n = pattern_len
                last_close = get_last_close(company_df, date_cursor)
                if last_close is None:
                    start_value = randint(100, 1000)
                else:
                    start_value = last_close
                print(
                    f"[PATTERN] start_value for {company} at {date_cursor}: {start_value} (pattern: {pattern_name})")
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
                    print(f"Erreur lors de l'insertion du pattern {pattern_name} : {e}")
                # --- PATCH DE SECURITE CONTINUITE & VALEURS ABERRANTES (STRICT) ---
                # Forcer la première valeur à start_value
                opens[0] = start_value
                closes[0] = start_value
                highs[0] = max(highs[0], start_value)
                lows[0] = min(lows[0], start_value)
                # Corriger les valeurs aberrantes (0, négatif, ou trop éloigné du start_value)
                for j in range(len(closes)):
                    for arr, name in zip([opens, highs, lows, closes],
                                         ["open", "high", "low", "close"]):
                        if arr[j] <= 0 or abs(arr[j] - start_value) > 10 * max(1, abs(start_value)):
                            print(
                                f"[WARNING] Correction valeur aberrante dans pattern {pattern_name} ({name}) : {arr[j]} -> {start_value}")
                            arr[j] = start_value
                # Vérification stricte de la cohérence du pattern (skip si n'importe quelle valeur s'éloigne de plus de 2x le start_value)
                max_dev = max([
                    max(abs(np.array(arr) - start_value)) for arr in [opens, highs, lows, closes]
                ])
                if max_dev > 2 * max(1, abs(start_value)):
                    print(
                        f"[SKIP PATTERN STRICT] Pattern {pattern_name} trop éloigné du start_value (max_dev={max_dev}), génération d'un trend classique à la place.")
                    # Générer un trend classique à la place
                    company_children, company_dataframes = generate_new_charts(
                        alpha=alpha,
                        length=sub_len,
                        start_value=start_value,
                        radio_trends=[trend],
                        companies=[company]
                    )
                    if company_dataframes and company_dataframes != no_update:
                        df_trend = pd.DataFrame(company_dataframes[0])
                        df_trend.index = trend_dates_i
                        # PATCH CONTINUITE : forcer la première valeur à start_value
                        for col in ['Open', 'High', 'Low', 'Close']:
                            if col in df_trend.columns:
                                if abs(df_trend[col].iloc[0] - start_value) > 1e-6:
                                    print(
                                        f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                                    df_trend.loc[df_trend.index[0], col] = start_value
                        for col in df_trend.columns:
                            company_df.loc[trend_dates_i, col] = df_trend[col].values
                        print(
                            f"[TREND] (remplacement pattern strict) last close for {company} at {date_cursor + sub_len - 1}: {df_trend['Close'].iloc[-1]}")
                    date_cursor += sub_len
                    continue
                # Vérification ultra-stricte : pas de drop > 30% ou pic > +30% du start_value
                closes_arr = np.array(closes)
                if np.any(closes_arr < 0.7 * start_value) or np.any(closes_arr > 1.3 * start_value):
                    print(
                        f'[SKIP PATTERN ULTRA-STRICT] Pattern {pattern_name} génère un drop ou pic trop important, remplacement par trend classique.')
                    company_children, company_dataframes = generate_new_charts(
                        alpha=alpha,
                        length=sub_len,
                        start_value=start_value,
                        radio_trends=[trend],
                        companies=[company]
                    )
                    if company_dataframes and company_dataframes != no_update:
                        df_trend = pd.DataFrame(company_dataframes[0])
                        df_trend.index = trend_dates_i
                        # PATCH CONTINUITE : forcer la première valeur à start_value
                        for col in ['Open', 'High', 'Low', 'Close']:
                            if col in df_trend.columns:
                                if abs(df_trend[col].iloc[0] - start_value) > 1e-6:
                                    print(
                                        f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                                    df_trend.loc[df_trend.index[0], col] = start_value
                        for col in df_trend.columns:
                            company_df.loc[trend_dates_i, col] = df_trend[col].values
                        print(
                            f"[TREND] (remplacement pattern ultra-strict) last close for {company} at {date_cursor + sub_len - 1}: {df_trend['Close'].iloc[-1]}")
                    date_cursor += sub_len
                    continue
                # Insérer le pattern sur la première partie de la sous-tranche
                pattern_dates = trend_dates_i[:pattern_len]
                df_pattern = pd.DataFrame({
                    "Open": opens,
                    "High": highs,
                    "Low": lows,
                    "Close": closes,
                    "adjclose": closes,
                    "Volume": [1000] * n
                }, index=pattern_dates)
                for col in df_pattern.columns:
                    company_df.loc[pattern_dates, col] = df_pattern[col].values
                print(
                    f"[PATTERN] last close for {company} at {date_cursor + pattern_len - 1}: {closes[-1]} (pattern: {pattern_name})")
                # Générer le reste de la sous-tranche avec generate_new_charts()
                if sub_len > pattern_len:
                    rest_dates = trend_dates_i[pattern_len:]
                    if len(rest_dates) > 0:
                        # On part du dernier close du pattern
                        last_close = closes[-1]
                        print(
                            f"[PATTERN->TREND] start_value for {company} at {date_cursor + pattern_len}: {last_close}")
                        company_children, company_dataframes = generate_new_charts(
                            alpha=alpha,
                            length=len(rest_dates),
                            start_value=last_close,
                            radio_trends=[trend],
                            companies=[company]
                        )
                        if company_dataframes and company_dataframes != no_update:
                            df_trend = pd.DataFrame(company_dataframes[0])
                            df_trend.index = rest_dates
                            # PATCH CONTINUITE : forcer la première valeur à last_close
                            for col in ['Open', 'High', 'Low', 'Close']:
                                if col in df_trend.columns:
                                    if abs(df_trend[col].iloc[0] - last_close) > 1e-6:
                                        print(
                                            f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {last_close}')
                                        df_trend.loc[df_trend.index[0], col] = last_close
                            for col in df_trend.columns:
                                company_df.loc[rest_dates, col] = df_trend[col].values
                            print(
                                f"[PATTERN->TREND] last close for {company} at {date_cursor + sub_len - 1}: {df_trend['Close'].iloc[-1]}")
                date_cursor += sub_len
                continue
        # Trend classique dans la sous-tranche
        last_close = get_last_close(company_df, date_cursor)
        if last_close is None:
            start_value = randint(100, 1000)
        else:
            start_value = last_close
        print(f"[TREND] start_value for {company} at {date_cursor}: {start_value}")
        company_children, company_dataframes = generate_new_charts(
            alpha=alpha,
            length=len(trend_dates_i),
            start_value=start_value,
            radio_trends=[trend],
            companies=[company]
        )
        if company_dataframes and company_dataframes != no_update:
            df_trend = pd.DataFrame(company_dataframes[0])
            df_trend.index = trend_dates_i
            # PATCH CONTINUITE : forcer la première valeur à start_value
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df_trend.columns:
                    if abs(df_trend[col].iloc[0] - start_value) > 1e-6:
                        print(
                            f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                        df_trend.loc[df_trend.index[0], col] = start_value
            for col in df_trend.columns:
                company_df.loc[trend_dates_i, col] = df_trend[col].values
            print(
                f"[TREND] last close for {company} at {date_cursor + sub_len - 1}: {df_trend['Close'].iloc[-1]}")
        date_cursor += sub_len


def handle_pattern_without(alpha, company, company_df, date_cursor, length, trend, trend_dates):
    last_close = get_last_close(company_df, date_cursor)
    if last_close is None:
        start_value = randint(100, 1000)
    else:
        start_value = last_close
    print(f"[WITHOUT] start_value for {company} at {date_cursor}: {start_value}")
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
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df_trend.columns:
                if abs(df_trend[col].iloc[0] - start_value) > 1e-6:
                    print(
                        f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                    df_trend.loc[df_trend.index[0], col] = start_value
        # Remplir la tranche dans le DataFrame global de la société
        for col in df_trend.columns:
            company_df.loc[trend_dates, col] = df_trend[col].values
        # Log de la dernière valeur générée
        print(
            f"[WITHOUT] last close for {company} at {date_cursor + len(trend_dates) - 1}: {df_trend['Close'].iloc[-1]}")
    date_cursor += length


def get_pattern_length(label):
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
    """
    Cherche la dernière valeur non-NaN de Close avant date_cursor
    """
    if date_cursor == 0:
        return None
    prev_closes = company_df['Close'].iloc[:date_cursor].dropna()
    if not prev_closes.empty:
        return prev_closes.iloc[-1]
    return None


def is_input_valid(size_data, start_date, end_date, granularity):
    return all([size_data, start_date, end_date, granularity])


def generate_date_range(start_date, end_date, granularity):
    return pd.date_range(start=start_date, end=end_date, freq=granularity)


def parse_size_data(size_data, global_length):
    alpha_map = {
        "Very Bull": 1000, "Medium Bull": 500, "Small Bull": 250,
        "Flat": 100,
        "Very Bear": 250, "Medium Bear": 500, "Small Bear": 1000
    }
    trends, alphas, lengths, pattern_types = [], [], [], []
    total_length = 0

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
    total = sum(lengths)
    if total == 0:
        return [0] * len(lengths)
    resized = [int(l / total * target) for l in lengths]
    diff = target - sum(resized)
    resized[-1] += diff
    return resized


def generate_company_dataframes(dates, companies, trends, alphas, lengths, pattern_types):
    company_dfs = {}
    for company in companies:
        company_df = pd.DataFrame(index=dates)
        date_cursor = 0
        for trend, alpha, length, pattern_type in zip(trends, alphas, lengths, pattern_types):
            trend_dates = dates[date_cursor:date_cursor + length]
            if pattern_type == "without":
                handle_pattern_without(alpha, company, company_df, date_cursor, length, trend, trend_dates)
            elif pattern_type == "with":
                handle_pattern_with(alpha, company, company_df, date_cursor, dates, length, trend)
            elif pattern_type is None:
                handle_pattern_none(company_df, date_cursor, dates, length, trend)
            date_cursor += length

        compute_indicators(company_df)
        company_dfs[company] = ensure_column_order(company_df)
    return company_dfs


def compute_indicators(df):
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
    expected_cols = ['Open', 'High', 'Low', 'Close', 'adjclose', 'Volume', 'long_MA', 'short_MA', '200_MA', 'RSI']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = np.nan
    return df[expected_cols]


def package_dataframe_for_export(company_dfs):
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
    graphs = []
    for company, df in company_dfs.items():
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
