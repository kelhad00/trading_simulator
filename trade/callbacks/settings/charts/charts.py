import json
import os
from random import randint
import dash
import pandas as pd
from dash import callback, Input, Output, State, html, no_update, dcc, page_registry, ALL
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import numpy as np
import dash_mantine_components as dmc
from trade.locales import translations as tls
from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.settings.display import display_chart
from trade.defaults import defaults as dlt
from trade.utils.graph.candlestick_charts import PLOTLY_CONFIG
from trade.callbacks.settings.charts.modal import generate_new_charts
from trade.callbacks.settings.charts.patterns_generator import insert_bullish_engulfing, insert_bearish_engulfing, insert_hammer, insert_shooting_star, insert_double_top, insert_head_and_shoulders, insert_double_bottom, insert_inverse_head_and_shoulders

# Mapping pattern -> paramètres optionnels
PATTERN_PARAMS = {
    "bullish_engulfing": [
        {"name": "amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
    ],
    "bearish_engulfing": [
        {"name": "amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
    ],
    "hammer": [
        {"name": "amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
    ],
    "shooting_star": [
        {"name": "amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
    ],
    "double_top": [
        {"name": "amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": "duree", "type": "number", "min": 3, "max": 10, "step": 1, "value": 5},
    ],
    "head_and_shoulders": [
        {"name": "amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": "duree", "type": "number", "min": 3, "max": 10, "step": 1, "value": 6},
    ],
    "double_bottom": [
        {"name": "amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": "duree", "type": "number", "min": 3, "max": 10, "step": 1, "value": 5},
    ],
    "inverse_head_and_shoulders": [
        {"name": "amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": "duree", "type": "number", "min": 3, "max": 10, "step": 1, "value": 6},
    ],
}




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
        print(df.shape[0])# Get the data of the selected company
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
    Input({'type': 'add-button', 'index': dash.ALL}, 'n_clicks'),
    State('timeline', 'children'),
    prevent_initial_call=True
)
def add_smash(*args):
    """
    Add a new item to the timeline when a button is clicked.
    
    Args:
        *args: Variable length argument list. The last argument is the current timeline children.
            - args[-1]: Current timeline children list
    """
    timeline_children = args[-1]

    if not dash.ctx.triggered:
        return timeline_children or []
    button_id = dash.ctx.triggered[0]['prop_id'].split('.')[0]
    button_id = json.loads(button_id)["index"]

    add_clicks = len(timeline_children or [])

    # Exemple d'ajout d'éléments dans la timeline
    new_item = html.Div(
        [tls[page_registry['lang']]["settings"]["charts"]["subtitles"][button_id],
         html.Div([
             dmc.Button(
                 "←",
                 id={'type': 'move-left', 'index': add_clicks},
                 color="dark",
                 size="xs",
                 variant="filled",
                 n_clicks=0,
                 style={'minWidth': '30px'}
             ),
             dmc.Button(
                 "→",
                 id={'type': 'move-right', 'index': add_clicks},
                 color="dark",
                 size="xs",
                 variant="filled",
                 n_clicks=0,
                 style={'minWidth': '30px'}
             ),
         ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '8px', 'padding': '8px'}),
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
            'backgroundColor': 'green' if 'Bull' in button_id else 'red' if 'Bear' in button_id else 'gray',
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
        id=f"item-{add_clicks}-{button_id}",
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
    for item in size_data:
        if size_data[item]["width"] == 0:
            continue
        length = size_data[item]["width"]
        label = size_data[item]["label"]
        alpha = alpha_map.get(label, 100)
        if "Bull" in label:
            trends.append("bull")
        elif "Bear" in label:
            trends.append("bear")
        else:
            trends.append("flat")
        alphas.append(alpha)
        lengths.append(length)
    if not trends:
        return html.Div(), None

    # Ajuster la somme des longueurs pour couvrir exactement la période
    total_length = sum(lengths)
    if total_length < len(dates):
        lengths[-1] += len(dates) - total_length
    elif total_length > len(dates):
        lengths[-1] -= total_length - len(dates)

    # Get all companies
    companies = []
    for key in dlt.companies_list.items():
        companies.append(key[0])  # Use the company symbol (key) instead of the dictionary
    if not companies:
        return html.Div(), None

    try:
        # Nouvelle logique : pour chaque société, construire un DataFrame indexé par toutes les dates
        company_dfs = {}
        for company in companies:
            company_df = pd.DataFrame(index=dates)
            date_cursor = 0
            for trend, alpha, length in zip(trends, alphas, lengths):
                trend_dates = dates[date_cursor:date_cursor+length]
                if len(trend_dates) == 0:
                    continue
                # Générer les données pour cette tranche
                company_children, company_dataframes = generate_new_charts(
                    alpha=alpha,
                    length=len(trend_dates),
                    start_value=randint(100,1000),
                    radio_trends=[trend],
                    companies=[company]
                )
                if company_dataframes and company_dataframes != no_update:
                    df_trend = pd.DataFrame(company_dataframes[0])
                    df_trend.index = trend_dates
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
    Input({'type': 'delete-button', 'index': dash.ALL}, 'n_clicks'),
    State('timeline', 'children'),
    prevent_initial_call=True
)
def delete_smash(delete_clicks, timeline_children):
    """
    Delete a timeline item based on button clicks.
    
    Args:
        delete_clicks (list): List of click counts for delete buttons
        timeline_children (list): Current list of timeline items
    """
    button_id = dash.ctx.triggered[0]['prop_id'].split('.')[0]
    index_to_delete = eval(button_id)['index']


    if (not dash.ctx.triggered) or sum(delete_clicks) == 0:
        return timeline_children or []
    # Supprimer l'élément correspondant
    timeline_items = timeline_children or []
    timeline_items.pop(index_to_delete)
    new_timeline = list()
    for i, item in enumerate(timeline_items):
        if i != item["props"]["children"][2]["props"]["id"]["index"]:
            item["props"]["children"][2]["props"]["id"]["index"] = i
            item["props"]["id"] = f"item-{i}"
        new_timeline.append(item)
    return new_timeline

@callback(
    Output('timeline', 'children', allow_duplicate=True),
    Input({'type': 'move-left', 'index': dash.ALL}, 'n_clicks'),
    Input({'type': 'move-right', 'index': dash.ALL}, 'n_clicks'),
    State('timeline', 'children'),
    prevent_initial_call=True
)
def move_item(left_clicks, right_clicks, timeline_children):
    """
    Move a timeline item left or right based on button clicks.
    
    Args:
        left_clicks (list): List of click counts for left movement buttons
        right_clicks (list): List of click counts for right movement buttons
        timeline_children (list): Current list of timeline items
        
    Returns:
        list: Updated timeline items with the moved item in its new position
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return timeline_children or []

    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    direction = 'left' if 'move-left' in ctx.triggered[0]['prop_id'] else 'right'
    index = button_id['index']

    if not (0 <= index < len(timeline_children)):
        return timeline_children

    timeline = timeline_children[:]
    if direction == 'left' and index > 0:
        timeline[index - 1], timeline[index] = timeline[index], timeline[index - 1]
    elif direction == 'right' and index < len(timeline) - 1:
        timeline[index + 1], timeline[index] = timeline[index], timeline[index + 1]

    for i, item in enumerate(timeline):
        item["props"]["id"] = f"item-{i}"
        arrow_div = item["props"]["children"][1]
        left_button = arrow_div["props"]["children"][0]
        right_button = arrow_div["props"]["children"][1]
        delete_button = item["props"]["children"][2]

        left_button["props"]["id"]["index"] = i
        right_button["props"]["id"]["index"] = i
        delete_button["props"]["id"]["index"] = i

    return timeline

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
    if not graph_data:
        raise PreventUpdate

    # --- Mise à jour de trade/defaults.py ---
    import re
    # Correction du chemin pour pointer vers le bon defaults.py (toujours dans trade/)
    defaults_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../defaults.py'))
    # Si le fichier n'existe pas, tente le chemin absolu depuis la racine du projet
    if not os.path.isfile(defaults_path):
        import sys
        import pathlib
        # Remonte jusqu'à trouver le dossier trade
        current = pathlib.Path(__file__).resolve()
        for parent in current.parents:
            candidate = parent / 'trade' / 'defaults.py'
            if candidate.exists():
                defaults_path = str(candidate)
                break
    try:
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
    except Exception as e:
        print(f'Erreur lors de la mise à jour de defaults.py : {e}')
    # --- Fin mise à jour ---

    try:
        # Reconstruire le DataFrame à partir des données
        # 1. Créer le DataFrame à partir du dict (colonnes simples)
        df = pd.DataFrame(graph_data['data'])
        # 2. Remettre le MultiIndex sur les colonnes
        df.columns = pd.MultiIndex.from_tuples(
            [tuple(col.split('|')) for col in graph_data['column_names']],
            names=['symbol', None]
        )
        # Ensure all expected columns for each company
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
        # 3. Remettre l'index (dates)
        df.index = pd.to_datetime(graph_data['index'])
        # S'assurer que toutes les sociétés et toutes les dates sont présentes
        all_symbols = df.columns.get_level_values('symbol').unique()
        freq = get_pandas_freq(granularity)
        all_dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        df = df.reindex(all_dates)
        # Sauvegarder le DataFrame complet dans un CSV global
        generated_data_path = os.path.join(dlt.data_path, 'generated_data.csv')
        df.to_csv(generated_data_path, index=True)
        return no_update
    except Exception as e:
        print('Error while exporting to CSV:', e)
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
    params = {id_["name"]: val for id_, val in zip(param_ids, param_values)} if param_ids else {}

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
    if pattern_name in ["bullish_engulfing", "bearish_engulfing"]:
        pattern_len = 2
    elif pattern_name in ["hammer", "shooting_star"]:
        pattern_len = 1
    else:
        pattern_len = params.get("duree", n)

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



