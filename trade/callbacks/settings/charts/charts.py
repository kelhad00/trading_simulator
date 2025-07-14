import os
import json
import os
from random import randint

import dash
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import callback, Input, Output, State, html, no_update, dcc, page_registry, ALL
from dash.exceptions import PreventUpdate

from trade.callbacks.settings.charts.modal import generate_new_charts
from trade.callbacks.settings.charts.patterns_generator import insert_bullish_engulfing, insert_bearish_engulfing, \
    insert_hammer, insert_shooting_star, insert_double_top, insert_head_and_shoulders, insert_double_bottom, \
    insert_inverse_head_and_shoulders
from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.graph.candlestick_charts import PLOTLY_CONFIG
from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.settings.display import display_chart

# Mapping pattern -> paramètres optionnels
PATTERN_PARAMS = {
    "bullish_engulfing": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
    ],
    "bearish_engulfing": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
    ],
    "hammer": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
    ],
    "shooting_star": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
    ],
    "double_top": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": tls[page_registry.get('lang', 'fr')]["settings"]["charts"]["subtitles"]["duration"], "type": "number", "min": 5, "max": 20, "step": 1, "value": 6},
    ],
    "head_and_shoulders": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": tls[page_registry.get('lang', 'fr')]["settings"]["charts"]["subtitles"]["duration"], "type": "number", "min": 5, "max": 20, "step": 1, "value": 6},
    ],
    "double_bottom": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": tls[page_registry.get('lang', 'fr')]["settings"]["charts"]["subtitles"]["duration"], "type": "number", "min": 5, "max": 20, "step": 1, "value": 6},
    ],
    "inverse_head_and_shoulders": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": tls[page_registry.get('lang', 'fr')]["settings"]["charts"]["subtitles"]["duration"], "type": "number", "min": 5, "max": 20, "step": 1, "value": 6},
    ],
}
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




@callback(
    Output("chart", "figure"),
    Input("select-company", "value"),
    Input("figures", "data"),
    prevent_initial_call=True
)
def update_graph(company, data):
    """
    Update the graph with the selected company
    Args:
        company: The selected company
        (data: (is only used to trigger the callback when new generated charts are stored in the csv file))
    Returns:
        The updated graph
    """
    try:
        df = get_generated_data()[company]
        return display_chart(df, 0, df.shape[0], company)  # Display the chart

    except Exception as e:
        print('Error while rendering chart :', e)
        return {"data": [], "layout": {}, "frames": []}


@callback(
    Output("modal", "opened", allow_duplicate=True),
    Output("modal-select-companies", "value"),
    Input("modify-button", "n_clicks"),
    State("modal", "opened"),
    State("select-company", "value"),
    prevent_initial_call=True
)
def open_modal(n, opened, company):
    """
    Open the modal to generate charts and automatically select the company in the dropdown
    """
    return not opened, [company]




@callback(
    Output("chart", "figure", allow_duplicate=True),
    Output("companies", "data", allow_duplicate=True),
    Input("button-delete-charts", "n_clicks"),
    State("select-company", "value"),
    State("companies", "data"),
    prevent_initial_call=True
)
def delete_revenues(n, company, companies):
    """
    Delete the revenues
    Args:
        n: The number of clicks
        company: The company selected
    Returns:
        The revenues
    """
    if company is None:
        raise PreventUpdate

    df = get_generated_data()
    symbols = df.columns.get_level_values('symbol').unique()
    if company in symbols:
        df = df.drop(company, axis=1, level='symbol')

    # Save data to single CSV file
    file_path = os.path.join(dlt.data_path, 'generated_data.csv')
    df.to_csv(file_path)

    companies[company]['got_charts'] = False

    return {"data": [], "layout": {}, "frames": []}, companies



#Edition graphique libre



@callback(
    Output('timeline', 'children', allow_duplicate=True),
    Input({'type': 'add-button', 'index': dash.ALL, 'pattern_type': ALL}, 'n_clicks'),
    State('timeline', 'children'),
    prevent_initial_call=True
)
def add_smash(*args):
    timeline_children = args[-1]

    if not dash.ctx.triggered:
        return timeline_children or []
    button_id = dash.ctx.triggered[0]['prop_id'].split('.')[0]
    button_id_dict = json.loads(button_id)
    label = button_id_dict["index"]
    pattern_type = button_id_dict.get("pattern_type", "with")
    type_label = "Avec pattern" if pattern_type == "with" else "Sans pattern"
    lang = page_registry.get('lang', 'fr')
    label_txt = tls[lang]["settings"]["charts"]["button"].get(label, label)
    # On retire 'Ajouter' ou 'Add' si présent au début du label
    if label_txt.startswith("Ajouter "):
        label_txt = label_txt[len("Ajouter ") :]
    elif label_txt.startswith("Add "):
        label_txt = label_txt[len("Add ") :]
    color = 'green' if 'Bull' in label else 'red' if 'Bear' in label else 'gray'
    add_clicks = len(timeline_children or [])
    new_item = html.Div(
        [
            html.Div([
                html.Strong(label_txt),
                html.Div(type_label, style={"fontSize": "0.8em", "fontWeight": 400, "marginTop": "2px"}),
            ]),
            dmc.Button(
                "Delete",
                id={'type': 'delete-button', 'index': add_clicks},
                color="red",
                size="xs",
                variant="filled",
                n_clicks=0,
                style={
                    'position': 'relative',
                    'bottom': '5px',
                    'right': '5px',
                    'width': '100%',
                    'marginTop': '4px'
                }
            )
        ],
        style={
            'width': '120px',
            'height': '120px',
            'backgroundColor': color,
            'display': 'flex',
            'color': 'white',
            'flexDirection': 'column',
            'justifyContent': 'space-between',
            'borderRadius': '8px',
            'padding': '8px',
            'margin': '4px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'resize': 'horizontal',
            'overflow': 'auto'
        },
        id=f"item-{add_clicks}-{label}",
    )
    timeline_items = timeline_children or []
    timeline_items.append(new_item)
    return timeline_items


# Utility function to convert user granularity to pandas frequency

def get_pandas_freq(granularity):
    if granularity == 'M':
        return 'ME'
    if granularity == 'H':
        return 'h'
    return granularity

@callback(
    Output("chart_new", "children"),
    Output("new-graph-df", "data"),
    Input('size-store', 'data'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('granularity-select', 'value'),
    State("new-graph-df", "data"),
    prevent_initial_call=True
)
def graph_preview_new(size_data, start_date, end_date, granularity, current_df):
    if not size_data or not start_date or not end_date or not granularity:
        return html.Div(), None
    # Génère la période à partir du picker et de la granularité
    freq = get_pandas_freq(granularity)
    dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    if len(dates) == 0:
        return html.Div(), None

    # Validation: period must be > 150 units of granularity
    if len(dates) <= 400:
        # Get language for translation
        try:
            lang = page_registry['lang']
            msg = tls[lang]["settings"]["charts"].get("alert_period_too_short", "La période de génération doit être supérieure à 400 unités de granularité.")
        except Exception:
            msg = "La période de génération doit être supérieure à 400 unités de granularité."
        return dmc.Alert(msg, color="red"), None

    # Map intensity levels to alpha values
    alpha_map = {
        "Very Bull": 1000,
        "Medium Bull": 500,
        "Small Bull": 250,
        "Flat": 100,
        "Very Bear": 250,
        "Medium Bear": 500,
        "Small Bear": 1000,
    }

    # Convert size_data to sequence of trends with appropriate alpha values
    trends = []
    alphas = []
    lengths = []
    pattern_types = []

    for item in size_data:
        if size_data[item]["width"] == 0:
            continue
        label = size_data[item]["label"]
        pattern_type = size_data[item].get("pattern_type", "with")
        alpha = alpha_map.get(label, 100)
        if "Bull" in label:
            trends.append("bull")
        elif "Bear" in label:
            trends.append("bear")
        else:
            trends.append(label)
        alphas.append(alpha)
        pattern_types.append(pattern_type)
        # Si pattern_type est None, on détermine dynamiquement la longueur du pattern généré
        if pattern_type is None:
            # Exemple : on suppose une fonction get_pattern_length(label) qui retourne la longueur du pattern
            pattern_length = get_pattern_length(label)
            lengths.append(pattern_length)
        else:
            lengths.append(size_data[item]["width"])
    if not trends:
        return html.Div(), None

    # Ajuster la somme des longueurs de façon proportionnelle pour couvrir exactement la période,
    # mais uniquement pour les longueurs dont pattern_type n'est pas None
    total_length = sum(lengths)
    n = len(lengths)
    # Indices des longueurs à ajuster
    idx_to_adjust = [i for i, pt in enumerate(pattern_types) if pt is not None]
    idx_fixed = [i for i, pt in enumerate(pattern_types) if pt is None]
    fixed_sum = sum(lengths[i] for i in idx_fixed)
    to_distribute = len(dates) - fixed_sum
    if to_distribute < 0:
        # Cas pathologique : les patterns fixes dépassent la période
        # On tronque le dernier pattern fixe
        lengths[idx_fixed[-1]] += to_distribute  # to_distribute est négatif
        to_distribute = 0
    if idx_to_adjust and total_length != len(dates):
        # Calculer la somme des longueurs à ajuster
        adjust_sum = sum(lengths[i] for i in idx_to_adjust)
        # Calculer les nouvelles longueurs proportionnelles pour les patterns à ajuster
        new_lengths = [int(round(lengths[i] * to_distribute / adjust_sum)) for i in idx_to_adjust]
        # Ajuster la dernière longueur pour compenser l'arrondi
        diff = to_distribute - sum(new_lengths)
        new_lengths[-1] += diff
        # Appliquer les nouvelles longueurs
        for idx, new_len in zip(idx_to_adjust, new_lengths):
            lengths[idx] = new_len

    # Get all companies
    companies = []
    for key in dlt.companies_list.items():
        companies.append(key[0])  # Use the company symbol (key) instead of the dictionar
        break
    if not companies:
        return html.Div(), None
    
    try:
        # Nouvelle logique : pour chaque société, construire un DataFrame indexé par toutes les dates
        company_dfs = {}
        for company in companies:
            company_df = pd.DataFrame(index=dates)
            date_cursor = 0
            for trend, alpha, length, pattern_type in zip(trends, alphas, lengths, pattern_types):
                trend_dates = dates[date_cursor:date_cursor+length]
                if len(trend_dates) == 0:
                    continue
                if pattern_type == "without" :
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
                        # PATCH CONTINUITE : forcer la première valeur à start_value
                        for col in ['Open', 'High', 'Low', 'Close']:
                            if col in df_trend.columns:
                                if abs(df_trend[col].iloc[0] - start_value) > 1e-6:
                                    print(f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                                    df_trend[col].iloc[0] = start_value
                        # Remplir la tranche dans le DataFrame global de la société
                        for col in df_trend.columns:
                            company_df.loc[trend_dates, col] = df_trend[col].values
                        # Log de la dernière valeur générée
                        print(f"[WITHOUT] last close for {company} at {date_cursor+len(trend_dates)-1}: {df_trend['Close'].iloc[-1]}")
                    date_cursor += length
                if pattern_type == "with":
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
                                print(f"[PATTERN] start_value for {company} at {date_cursor}: {start_value} (pattern: {pattern_name})")
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
                                for i in range(len(closes)):
                                    for arr, name in zip([opens, highs, lows, closes], ["open", "high", "low", "close"]):
                                        if arr[i] <= 0 or abs(arr[i] - start_value) > 10 * max(1, abs(start_value)):
                                            print(f"[WARNING] Correction valeur aberrante dans pattern {pattern_name} ({name}) : {arr[i]} -> {start_value}")
                                            arr[i] = start_value
                                # Vérification stricte de la cohérence du pattern (skip si n'importe quelle valeur s'éloigne de plus de 2x le start_value)
                                max_dev = max([
                                    max(abs(np.array(arr) - start_value)) for arr in [opens, highs, lows, closes]
                                ])
                                if max_dev > 2 * max(1, abs(start_value)):
                                    print(f"[SKIP PATTERN STRICT] Pattern {pattern_name} trop éloigné du start_value (max_dev={max_dev}), génération d'un trend classique à la place.")
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
                                                    print(f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                                                    df_trend[col].iloc[0] = start_value
                                        for col in df_trend.columns:
                                            company_df.loc[trend_dates_i, col] = df_trend[col].values
                                        print(f"[TREND] (remplacement pattern strict) last close for {company} at {date_cursor+sub_len-1}: {df_trend['Close'].iloc[-1]}")
                                    date_cursor += sub_len
                                    continue
                                # Vérification ultra-stricte : pas de drop > 30% ou pic > +30% du start_value
                                closes_arr = np.array(closes)
                                if np.any(closes_arr < 0.7 * start_value) or np.any(closes_arr > 1.3 * start_value):
                                    print(f'[SKIP PATTERN ULTRA-STRICT] Pattern {pattern_name} génère un drop ou pic trop important, remplacement par trend classique.')
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
                                                    print(f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                                                    df_trend.loc[df_trend.index[0], col] = start_value
                                        for col in df_trend.columns:
                                            company_df.loc[trend_dates_i, col] = df_trend[col].values
                                        print(f"[TREND] (remplacement pattern ultra-strict) last close for {company} at {date_cursor+sub_len-1}: {df_trend['Close'].iloc[-1]}")
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
                                print(f"[PATTERN] last close for {company} at {date_cursor+pattern_len-1}: {closes[-1]} (pattern: {pattern_name})")
                                # Générer le reste de la sous-tranche avec generate_new_charts()
                                if sub_len > pattern_len:
                                    rest_dates = trend_dates_i[pattern_len:]
                                    if len(rest_dates) > 0:
                                        # On part du dernier close du pattern
                                        last_close = closes[-1]
                                        print(f"[PATTERN->TREND] start_value for {company} at {date_cursor+pattern_len}: {last_close}")
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
                                                        print(f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {last_close}')
                                                        df_trend[col].iloc[0] = last_close
                                            for col in df_trend.columns:
                                                company_df.loc[rest_dates, col] = df_trend[col].values
                                            print(f"[PATTERN->TREND] last close for {company} at {date_cursor+sub_len-1}: {df_trend['Close'].iloc[-1]}")
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
                                        print(f'[PATCH CONTINUITE] Correction {col} première valeur {df_trend[col].iloc[0]} -> {start_value}')
                                        df_trend[col].iloc[0] = start_value
                            for col in df_trend.columns:
                                company_df.loc[trend_dates_i, col] = df_trend[col].values
                            print(f"[TREND] last close for {company} at {date_cursor+sub_len-1}: {df_trend['Close'].iloc[-1]}")
                        date_cursor += sub_len

                if pattern_type is None:
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

                    # Appeler la bonne fonction d'insertion
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


            # Ensure all expected columns are present and in the correct order
            expected_cols = ['Open', 'High', 'Low', 'Close', 'adjclose', 'Volume', 'long_MA', 'short_MA', '200_MA', 'RSI']
            # Calcul des moyennes mobiles et du RSI
            if 'Close' in company_df.columns:
                company_df['short_MA'] = company_df['Close'].rolling(window=20, min_periods=1).mean()
                company_df['long_MA'] = company_df['Close'].rolling(window=50, min_periods=1).mean()
                company_df['200_MA'] = company_df['Close'].rolling(window=200, min_periods=1).mean()
                # RSI
                delta = company_df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
                rs = gain / (loss + 1e-9)
                company_df['RSI'] = 100 - (100 / (1 + rs))
            for col in expected_cols:
                if col not in company_df.columns:
                    company_df[col] = np.nan
            company_df = company_df[expected_cols]
            company_dfs[company] = company_df
        # Concaténer tous les DataFrames de sociétés sur les colonnes (MultiIndex)
        df_global = pd.concat(company_dfs.values(), axis=1, keys=company_dfs.keys(), names=['symbol'])
        # Préparer les données pour l'export
        data_dict = {
            'data': {f'{col[0]}|{col[1]}': [str(x) if isinstance(x, (pd.Timestamp, np.datetime64)) else x for x in df_global[col]] for col in df_global.columns},
            'column_names': [f'{col[0]}|{col[1]}' for col in df_global.columns],
            'index': [str(x) if isinstance(x, (pd.Timestamp, np.datetime64)) else x for x in df_global.index]
        }
        # Générer les graphiques de preview pour les premières sociétés (candlestick)
        children = []
        for i, (company, df) in enumerate(company_dfs.items()):
            # On cherche les colonnes OHLC (open, high, low, close)
            o_col = next((col for col in df.columns if str(col).lower() == 'open'), None)
            h_col = next((col for col in df.columns if str(col).lower() == 'high'), None)
            l_col = next((col for col in df.columns if str(col).lower() == 'low'), None)
            c_col = next((col for col in df.columns if str(col).lower() == 'close'), None)
            fig = go.Figure()
            if all([o_col, h_col, l_col, c_col]):
                fig.add_trace(go.Candlestick(
                    x=[str(x) for x in df.index],
                    open=df[o_col],
                    high=df[h_col],
                    low=df[l_col],
                    close=df[c_col],
                    name=f"{company}"
                ))
            else:
                fig.add_trace(go.Scatter(x=[], y=[], name="No OHLC"))
                fig.update_layout(title=f"Erreur: pas de colonnes OHLC pour {company}")
            fig.update_layout(title=f"Prévisualisation {company}", xaxis_title="Date", yaxis_title="Cours")
            children.append(dcc.Graph(figure=fig, config=PLOTLY_CONFIG))
        if not children:
            return html.Div(), None
        # Ajout d'un wrapper scrollable autour de la preview
        return html.Div(children, style={"overflowY": "auto", "maxHeight": "80vh"}), data_dict
    except Exception as e:
        return html.Div(), None



@callback(
    Output('timeline', 'children', allow_duplicate=True),
    Output('size-store', 'data', allow_duplicate=True),
    Input({'type': 'delete-button', 'index': dash.ALL}, 'n_clicks'),
    State('timeline', 'children'),
    State('size-store', 'data'),
    prevent_initial_call=True
)
def delete_smash(delete_clicks, timeline_children, size_data):
    """
    Delete a timeline item based on button clicks and synchronise with size_data.
    Args:
        delete_clicks (list): List of click counts for delete buttons
        timeline_children (list): Current list of timeline items
        size_data (dict): Current size_data
    """
    button_id = dash.ctx.triggered[0]['prop_id'].split('.')[0]
    index_to_delete = eval(button_id)['index']

    if (not dash.ctx.triggered) or sum(delete_clicks) == 0:
        return timeline_children or [], size_data
    # Supprimer l'élément correspondant dans la timeline
    timeline_items = timeline_children or []
    timeline_items.pop(index_to_delete)
    new_timeline = list()
    for i, item in enumerate(timeline_items):
        # Le bouton Delete est maintenant à l'index 1
        if i != item["props"]["children"][1]["props"]["id"]["index"]:
            item["props"]["children"][1]["props"]["id"]["index"] = i
            item["props"]["id"] = f"item-{i}"
        new_timeline.append(item)
    # Supprimer l'entrée correspondante dans size_data (en respectant l'ordre)
    if size_data and isinstance(size_data, dict):
        keys = list(size_data.keys())
        if 0 <= index_to_delete < len(keys):
            del size_data[keys[index_to_delete]]

    print(size_data)
    
    return new_timeline, size_data

@callback(
    Output("chart", "figure", allow_duplicate=True),
    Input("modify-button-new-graph", "n_clicks"),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('granularity-select', 'value'),
    State("new-graph-df", "data"),
    prevent_initial_call=True
)
def export_to_csv(n, start_date, end_date, granularity, graph_data):
    """
    Export all companies data to CSV when the modify button is clicked.
    Also updates start_date and granularity in trade/defaults.py.
    Args:
        n (int): Number of clicks on the modify button
        start_date (str): Selected start date
        granularity (str): Selected granularity
        graph_data (dict): Dictionary containing all companies data in simplified format
    Returns:
        dict: No update to the current chart figure if successful, or error message if failed
    Raises:
        PreventUpdate: If graph_data is empty
    """
    print("[EXPORT] Début export_to_csv")
    print(f"[EXPORT] start_date={start_date}, end_date={end_date}, granularity={granularity}")
    print(f"[EXPORT] graph_data keys: {list(graph_data.keys()) if graph_data else 'AUCUNE'}")
    if not graph_data:
        print("[EXPORT] graph_data est vide, PreventUpdate")
        raise PreventUpdate

    # --- Mise à jour de trade/defaults.py ---
    defaults_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../defaults.py'))
    if not os.path.isfile(defaults_path):
        import pathlib
        current = pathlib.Path(__file__).resolve()
        for parent in current.parents:
            candidate = parent / 'trade' / 'defaults.py'
            if candidate.exists():
                defaults_path = str(candidate)
                break
    try:
        print(f"[EXPORT] Ouverture de {defaults_path} pour mise à jour")
        with open(defaults_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith('start_date'):
                new_lines.append(f'    start_date = "{start_date}" \n')
            elif line.strip().startswith('granularity'):
                new_lines.append(f'    granularity = "{granularity}" \n')
            else:
                new_lines.append(line)
        with open(defaults_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("[EXPORT] defaults.py mis à jour")
    except Exception as e:
        print(f'[EXPORT] Erreur lors de la mise à jour de defaults.py : {e}')
    # --- Fin mise à jour ---

    try:
        print("[EXPORT] Reconstruction du DataFrame à partir de graph_data")
        df = pd.DataFrame(graph_data['data'])
        print(f"[EXPORT] Colonnes du DataFrame: {df.columns}")
        df.columns = pd.MultiIndex.from_tuples(
            [tuple(col.split('|')) for col in graph_data['column_names']],
            names=['symbol', None]
        )
        print(f"[EXPORT] MultiIndex columns: {df.columns}")
        expected_cols = ['Open', 'High', 'Low', 'Close', 'adjclose', 'Volume', 'long_MA', 'short_MA', '200_MA', 'RSI']
        all_symbols = df.columns.get_level_values('symbol').unique()
        new_cols = []
        for symbol in all_symbols:
            for col in expected_cols:
                new_cols.append((symbol, col))
        for col in new_cols:
            if col not in df.columns:
                df[col] = np.nan
        df = df.reindex(columns=new_cols)
        print(f"[EXPORT] Colonnes après reindex: {df.columns}")
        df.index = pd.to_datetime(graph_data['index'])
        print(f"[EXPORT] Index du DataFrame: {df.index}")
        all_symbols = df.columns.get_level_values('symbol').unique()
        freq = get_pandas_freq(granularity)
        all_dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        print(f"[EXPORT] all_dates: {all_dates}")
        df = df.reindex(all_dates)
        generated_data_path = os.path.join(dlt.data_path, 'generated_data.csv')
        print(f"[EXPORT] Sauvegarde du DataFrame dans {generated_data_path}")
        df.to_csv(generated_data_path, index=True)
        print("[EXPORT] Export terminé avec succès !")
        return no_update
    except Exception as e:
        print('Error while exporting to CSV:', e)
        import traceback
        traceback.print_exc()
        return no_update

@callback(
    Output("pattern-preview-graph", "figure"),
    Input("pattern-select", "value"),
    Input({"type": "pattern-param", "name": ALL}, "value"),
    State({"type": "pattern-param", "name": ALL}, "id"),
)
def update_pattern_preview(pattern_name, param_values, param_ids):
    if not pattern_name:
        return go.Figure()

    # Préparer les paramètres sous forme de dict
    def normalize_key(key):
        key = key.lower()
        if key in ("duration", "durée"):
            return "duree"
        elif key == "amplitude":
            return "amplitude"
        return key

    params = {normalize_key(id_["name"]): val for id_, val in zip(param_ids, param_values)} if param_ids else {}

    # Générer les données OHLC pour chaque pattern
    n = 6  # nombre de jours max pour les patterns
    opens = [100.0] * n
    highs = [100.0] * n
    lows = [100.0] * n
    closes = [100.0] * n

    # Appel de la bonne fonction
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
        else:
            return go.Figure()
    except Exception as e:
        return go.Figure(layout={"title": f"Erreur : {e}"})

    # Déterminer la longueur utile dynamiquement
    def get_pattern_length_preview(pattern_name, params):
        import os
        import json
        from trade.defaults import defaults as dlt
        file_path = os.path.join(dlt.data_path, "pattern_configs.json")
        pattern_key = pattern_name.lower()
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
        return params.get("duree", n)

    pattern_len = get_pattern_length_preview(pattern_name, params)

    # Récupérer la langue courante
    lang = page_registry['lang']
    # Récupérer les labels traduits
    preview_label = tls[lang]["settings"]["charts"]["subtitles"]["preview_pattern_title"]
    day_label = tls[lang]["settings"]["charts"]["subtitles"]["preview_pattern_day"]
    price_label = tls[lang]["settings"]["charts"]["subtitles"]["preview_pattern_price"]

    # Générer le graphique
    fig = go.Figure(data=[
        go.Candlestick(
            open=opens[:pattern_len],
            high=highs[:pattern_len],
            low=lows[:pattern_len],
            close=closes[:pattern_len],
            increasing_line_color='green',
            decreasing_line_color='red',
            showlegend=False
        ),
        go.Scatter(
            x=list(range(pattern_len)),
            y=closes[:pattern_len],
            mode='lines+markers',
            name='Close',
            line=dict(color='blue', width=2, dash='dash'),
            marker=dict(size=6, color='blue')
        )
    ])
    fig.update_layout(
        xaxis_title=day_label,
        yaxis_title=price_label,
        title=f"{preview_label} {pattern_name.replace('_', ' ').title()}",
        xaxis=dict(tickvals=list(range(pattern_len)), ticktext=[f"{day_label} {i+1}" for i in range(pattern_len)])
    )
    return fig

@callback(
    Output("save-pattern-config-msg", "children"),
    Input("save-pattern-config-btn", "n_clicks"),
    State("pattern-select", "value"),
    State({"type": "pattern-param", "name": ALL}, "value"),
    State({"type": "pattern-param", "name": ALL}, "id"),
    prevent_initial_call=True
)
def save_pattern_config(n_clicks, pattern_name, param_values, param_ids):
    # Récupérer la langue courante
    lang = page_registry['lang']
    if not pattern_name:
        try:
            msg = tls[lang]["settings"]["charts"]["alert_select_pattern"]
        except Exception:
            msg = "Veuillez sélectionner un pattern."
        return dmc.Alert(msg, color="red")
    params = {id_["name"]: val for id_, val in zip(param_ids, param_values)} if param_ids else {}
    file_path = os.path.join(dlt.data_path, "pattern_configs.json")
    # Charger l'existant
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
    except Exception:
        configs = {}
    # Mettre à jour la config du pattern
    configs[pattern_name] = params
    # Sauvegarder
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2)
    try:
        msg = tls[lang]["settings"]["charts"]["alert_config_saved"]
    except Exception:
        msg = "Configuration sauvegardée !"
    return dmc.Alert(msg, color="green")

# Callback pour synchroniser dynamiquement la valeur affichée à droite de chaque slider
@callback(
    Output({"type": "pattern-param-value", "name": ALL}, "children"),
    Input({"type": "pattern-param", "name": ALL}, "value"),
    State({"type": "pattern-param", "name": ALL}, "id"),
)
def update_pattern_param_values(values, ids):
    # Retourne la valeur sous forme de string pour chaque slider
    return [str(v) for v in values]

@callback(
    Output("pattern-params-container", "children"),
    Input("pattern-select", "value"),
    Input("reset-pattern-config-btn", "n_clicks"),
    State({"type": "pattern-param", "name": ALL}, "value"),
    State({"type": "pattern-param", "name": ALL}, "id"),
    prevent_initial_call=True
)
def update_pattern_params(pattern_name, reset_clicks, current_values, current_ids):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    if not pattern_name:
        return []
    params = PATTERN_PARAMS.get(pattern_name, [])
    if not params:
        return [html.Div("Aucun paramètre optionnel pour ce pattern.")]
    file_path = os.path.join(dlt.data_path, "pattern_configs.json")
    configs = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
    except Exception:
        configs = {}
    lang = page_registry['lang']
    if triggered == "reset-pattern-config-btn":
        value_map = {param["name"]: param["value"] for param in params}
        configs[pattern_name] = value_map
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(configs, f, indent=2)
    elif pattern_name in configs:
        value_map = {param["name"]: configs[pattern_name].get(param["name"], param["value"]) for param in params}
    else:
        value_map = {id_["name"]: val for id_, val in zip(current_ids, current_values)} if current_ids else {param["name"]: param["value"] for param in params}
    fields = []
    for param in params:
        value = value_map.get(param["name"], param["value"])
        try:
            label = tls[lang]["settings"]["charts"]["patterns_params"][pattern_name][param["name"]]
        except Exception:
            label = param["name"]
        if param["type"] == "number":
            fields.append(
                html.Div([
                    dmc.Text(label, size="sm", className="mb-1"),
                    dmc.Slider(
                        id={"type": "pattern-param", "name": param["name"]},
                        value=value,
                        min=param["min"],
                        max=param["max"],
                        step=param["step"],
                        marks=[
                            {"value": param["min"], "label": str(param["min"])} if param["min"] != param["max"] else {},
                            {"value": param["max"], "label": str(param["max"])} if param["min"] != param["max"] else {},
                        ],
                        size="md",
                        className="mb-4 w-64",
                        labelAlwaysOn=False,
                    ),
                ], style={"marginBottom": "16px"})
            )
    return fields

@callback(
    Output('timeline', 'children', allow_duplicate=True),
    Input('add-pattern-button', 'n_clicks'),
    State(  'pattern-selector', 'value'),
    State('timeline', 'children'),
    State({'type': 'pattern-section', 'pattern_type': ALL}, 'id'),
    prevent_initial_call=True
)
def add_pattern_block(n_clicks, selected_pattern, timeline_children, section_ids):
    if not selected_pattern:
        raise PreventUpdate
    # Toujours une liste
    if not isinstance(timeline_children, list):
        timeline_items = []
    else:
        timeline_items = timeline_children
    lang = page_registry.get('lang', 'fr')
    tl = tls[lang]["settings"]["charts"]["patterns_names"]
    pattern_colors = {
        "bullish_engulfing": "green",
        "bearish_engulfing": "red",
        "hammer": "orange",
        "shooting_star": "purple",
        "double_top": "#b91c1c",
        "head_and_shoulders": "#6366f1",
        "double_bottom": "#059669",
        "inverse_head_and_shoulders": "#2563eb",
    }
    label = tl.get(selected_pattern, selected_pattern)
    color = pattern_colors.get(selected_pattern, "gray")
    index = len(timeline_items)
    # Déterminer le pattern_type (with/without) selon la section active
    pattern_type = "with"
    for section in section_ids:
        if section and isinstance(section, dict) and section.get("pattern_type") == "without":
            pattern_type = "without"
            break
    new_item = make_timeline_block(label, color, index, pattern_id=selected_pattern, pattern_type="dont")
    timeline_items.append(new_item)
    return timeline_items


def make_timeline_block(label, color, index, pattern_id=None, pattern_type="with"):
    # pattern_id: si fourni, utilisé pour l'id du bloc (sinon label)
    type_label = "Avec pattern" if pattern_type == "with" else "Sans pattern" if pattern_type != "dont" else None
    return html.Div(
        [
            html.Div([
                html.Strong(label),
                html.Div(type_label, style={
                    "fontSize": "0.8em",
                    "fontWeight": 400,
                    "marginTop": "2px"
                }) if type_label is not None else None,
            ]),
            dmc.Button(
                "Delete",
                id={'type': 'delete-button', 'index': index},
                color="red",
                size="xs",
                variant="filled",
                n_clicks=0,
                style={
                    'position': 'relative',
                    'bottom': '5px',
                    'right': '5px',
                    'width': '100%',
                    'marginTop': '4px'
                }
            )
        ],
        style={
            'width': '120px',
            'height': '120px',
            'backgroundColor': color,
            'display': 'flex',
            'color': 'white',
            'flexDirection': 'column',
            'justifyContent': 'space-between',
            'borderRadius': '8px',
            'padding': '8px',
            'margin': '4px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'resize': 'horizontal',
            'overflow': 'auto'
        },
        id=f"item-{index}-{pattern_id if pattern_id else label}",
    )

def get_pattern_length(label):
    # Utilise pattern_configs.json si disponible
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

# --- Utilitaire pour continuité ---
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
