import json
import os
from random import randint
import csv

import dash
import pandas as pd
from dash import callback, Input, Output, State, html, no_update, dcc, page_registry
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from pandas import DataFrame
import numpy as np
import dash_mantine_components as dmc
from trade.locales import translations as tls
from trade.utils.market import get_first_timestamp
from trade.utils.settings.create_market_data import get_generated_data, export_generated_data
from trade.utils.settings.display import display_chart
from trade.defaults import defaults as dlt
from trade.utils.graph.candlestick_charts import PLOTLY_CONFIG
from trade.callbacks.settings.charts.modal import generate_new_charts
from trade.callbacks.settings.charts.patterns_generator import insert_bullish_engulfing, insert_bearish_engulfing, insert_hammer, insert_shooting_star, insert_double_top, insert_head_and_shoulders
from dash import ALL

# Mapping pattern -> paramètres optionnels
PATTERN_PARAMS = {
    "bullish_engulfing": [
        {"name": "down1", "label": "Baisse jour 1 (%)", "type": "number", "min": 0.98, "max": 1.0, "step": 0.001, "value": 0.995},
        {"name": "up1", "label": "Hausse jour 2 (%)", "type": "number", "min": 1.0, "max": 1.02, "step": 0.001, "value": 1.005},
    ],
    "bearish_engulfing": [
        {"name": "down1", "label": "Baisse jour 2 (%)", "type": "number", "min": 0.98, "max": 1.0, "step": 0.001, "value": 0.995},
        {"name": "up1", "label": "Hausse jour 1 (%)", "type": "number", "min": 1.0, "max": 1.02, "step": 0.001, "value": 1.005},
    ],
    "hammer": [
        {"name": "low", "label": "Corps min (%)", "type": "number", "min": 0.001, "max": 0.01, "step": 0.001, "value": 0.001},
        {"name": "high", "label": "Corps max (%)", "type": "number", "min": 0.002, "max": 0.02, "step": 0.001, "value": 0.003},
    ],
    "shooting_star": [
        {"name": "low", "label": "Corps min (%)", "type": "number", "min": 0.001, "max": 0.01, "step": 0.001, "value": 0.001},
        {"name": "high", "label": "Corps max (%)", "type": "number", "min": 0.002, "max": 0.02, "step": 0.001, "value": 0.003},
    ],
    "double_top": [
        {"name": "top_init", "label": "Sommet initial (%)", "type": "number", "min": 1.0, "max": 1.05, "step": 0.001, "value": 1.02},
        {"name": "creux_init", "label": "Creux initial (%)", "type": "number", "min": 1.0, "max": 1.05, "step": 0.001, "value": 1.01},
        {"name": "rise1", "label": "Hausse 1 (%)", "type": "number", "min": 1.0, "max": 1.05, "step": 0.001, "value": 1.015},
        {"name": "low4", "label": "Bas 4 (%)", "type": "number", "min": 0.98, "max": 1.01, "step": 0.001, "value": 0.998},
        {"name": "high4", "label": "Haut 4 (%)", "type": "number", "min": 1.0, "max": 1.01, "step": 0.001, "value": 1.002},
        {"name": "close5", "label": "Clôture 5 (%)", "type": "number", "min": 0.95, "max": 1.0, "step": 0.001, "value": 0.99},
    ],
    "head_and_shoulders": [
        {"name": "shoulder_rate", "label": "Épaule (%)", "type": "number", "min": 1.0, "max": 1.05, "step": 0.001, "value": 1.02},
        {"name": "head_rate", "label": "Tête (%)", "type": "number", "min": 1.0, "max": 1.1, "step": 0.001, "value": 1.04},
        {"name": "neckline_rate", "label": "Ligne de cou (%)", "type": "number", "min": 0.95, "max": 1.0, "step": 0.001, "value": 0.99},
        {"name": "breaking_rate", "label": "Cassure (%)", "type": "number", "min": 0.9, "max": 1.0, "step": 0.001, "value": 0.97},
    ],
}

# Callback pour générer dynamiquement les champs de paramètres
from dash import Output, Input, State, callback

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
    # Utiliser un fichier JSON pour stocker les configs
    file_path = os.path.join(dlt.data_path, "pattern_configs.json")
    configs = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            configs = json.load(f)
    except Exception:
        configs = {}
    if triggered == "reset-pattern-config-btn":
        # On force les valeurs par défaut ET on écrase le JSON
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
        if param["type"] == "number":
            fields.append(
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
                    labelAlwaysOn=True,
                )
            )
    return fields

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
        df = get_generated_data()[company]  # Get the data of the selected company
        return display_chart(df, 0, df.shape[0], company)  # Display the chart

    except Exception as e:
        print('Error while rendering chart :', e)
        return {"data": [], "layout": {}, "frames": []}


@callback(
    Output("modal", "opened"),
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


@callback(
    Output("chart_new", "children"),
    Output("new-graph-df", "data"),
    Input('size-store', 'data'),
    State("new-graph-df", "data"),
    prevent_initial_call=True
)
def graph_preview_new(size_data, current_df):
    """
    Generate a preview of charts based on the size data and current DataFrame.
    
    Args:
        size_data (dict): Dictionary containing size and trend information for each timeline item
        current_df (dict): Current DataFrame data in a serializable format
        
    Returns:
        tuple: (html.Div, dict)
            - html.Div containing the generated chart previews
            - Dictionary containing the serialized DataFrame data
    """
    if not size_data:
        return html.Div(), {}
    
    first_timestamp = get_first_timestamp(get_generated_data())

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
        return html.Div(), {}

    # Get all companies
    companies = []
    for key in dlt.companies_list.items():
            companies.append(key[0])  # Use the company symbol (key) instead of the dictionary

    if not companies:
        return html.Div(), {}

    try:
        # Get existing data to get the date range
        existing_df = get_generated_data()
        if existing_df.empty:
            return html.Div(), {}

        # Get the date range
        dates = existing_df.index

        # Calculate proportions for each trend
        total_width = sum(lengths)
        proportions = [length/total_width for length in lengths]

        # Divide dates according to proportions
        date_ranges = []
        start_idx = 0
        for prop in proportions:
            end_idx = start_idx + int(prop * len(dates))
            date_ranges.append(dates[start_idx:end_idx])
            start_idx = end_idx

        # Generate charts for each trend
        children = []
        all_dataframes = {}  # To store data for all companies

        for i, (trend, alpha, date_range) in enumerate(zip(trends, alphas, date_ranges)):
            trend_children = []
            dataframes = []
            for company in companies:
                # First generate the base chart data
                company_children, company_dataframes = generate_new_charts(
                    alpha=alpha,
                    length=len(date_range),
                    start_value=randint(100,1000),
                    radio_trends=[trend],
                    companies=[company]
                )

                if company_children is no_update or company_dataframes is no_update:
                    continue

                if company_children and company_dataframes:
                    # Process each dataframe
                    for df_dict in company_dataframes:
                        # Convert to DataFrame for easier manipulation
                        df = pd.DataFrame(df_dict)

                        # Convert DataFrame columns to numpy arrays for manipulation
                        opens = df['Open'].values
                        highs = df['High'].values
                        lows = df['Low'].values
                        closes = df['Close'].values

                        # Define pattern spans
                        pattern_span = {
                            "bullish_engulfing": 2,
                            "bearish_engulfing": 2,
                            "hammer": 1,
                            "shooting_star": 1,
                            "double_top": 5,
                            "head_and_shoulders": 5
                        }

                        # Keep track of used days to avoid overlap
                        used_days = set()
                        # Store patterns to apply them later during visualization
                        patterns_to_apply = []

                        # Try to add patterns multiple times
                        num_attempts = len(opens) // 10  # Try to add a pattern every 10 days on average

                        for _ in range(num_attempts):
                            if np.random.random() < 0.4:  # 40% chance for each attempt
                                # Select pattern based on current trend
                                if trend == "bull":
                                    pattern = np.random.choice(["bullish_engulfing", "hammer"], p=[0.6, 0.4])
                                elif trend == "bear":
                                    pattern = np.random.choice(["bearish_engulfing", "shooting_star", "double_top"], p=[0.4, 0.3, 0.3])
                                else:  # flat trend
                                    pattern = np.random.choice(["head_and_shoulders", None], p=[0.3, 0.7])

                                if pattern:
                                    # Get span for this pattern
                                    span = pattern_span[pattern]

                                    # Find a suitable position for the pattern
                                    # Leave some margin at the start and end
                                    margin = 5
                                    possible_starts = list(range(margin, len(opens) - span - margin))

                                    # Remove positions that would overlap with existing patterns
                                    possible_starts = [
                                        pos for pos in possible_starts
                                        if not any(
                                            day in used_days
                                            for day in range(pos - 2, pos + span + 2)  # Add buffer around patterns
                                        )
                                    ]

                                    if possible_starts:  # If we found a valid position
                                        pattern_day = np.random.choice(possible_starts)
                                        pattern_date = date_range[pattern_day]

                                        # Mark these days as used
                                        for day in range(pattern_day - 2, pattern_day + span + 2):
                                            used_days.add(day)

                                        # Apply the pattern
                                        if pattern == "bullish_engulfing":
                                            insert_bullish_engulfing(opens, highs, lows, closes, pattern_day)
                                        elif pattern == "bearish_engulfing":
                                            insert_bearish_engulfing(opens, highs, lows, closes, pattern_day)
                                        elif pattern == "hammer":
                                            insert_hammer(opens, highs, lows, closes, pattern_day)
                                        elif pattern == "shooting_star":
                                            insert_shooting_star(opens, highs, lows, closes, pattern_day)
                                        elif pattern == "double_top":
                                            insert_double_top(opens, highs, lows, closes, pattern_day)
                                        elif pattern == "head_and_shoulders":
                                            insert_head_and_shoulders(opens, highs, lows, closes, pattern_day)

                                        # Store pattern info for later visualization
                                        patterns_to_apply.append({
                                            'pattern': pattern,
                                            'day': pattern_day,
                                            'span': span,
                                            'date': pattern_date
                                        })

                        # Update the DataFrame with modified values
                        df['Open'] = opens
                        df['High'] = highs
                        df['Low'] = lows
                        df['Close'] = closes

                        # Convert to dict and store patterns
                        new_dict = df.to_dict('list')
                        new_dict['_patterns'] = patterns_to_apply
                        dataframes.append(new_dict)

                    trend_children.extend(company_children)

            if trend_children and dataframes:
                # For each chart, update the dates
                children = []  # List to store the new graphs
                for j, df_dict in enumerate(dataframes):
                    # Extract patterns before creating DataFrame
                    patterns_info = df_dict.pop('_patterns', [])

                    # Create DataFrame from the data
                    df = pd.DataFrame(df_dict)
                    date_index = pd.date_range(start=first_timestamp, periods=df.shape[0], freq='D')
                    df.set_index(date_index, inplace=True)

                    # Store data in the global dictionary
                    company = companies[j]
                    if company not in all_dataframes:
                        all_dataframes[company] = df
                    else:
                        # Concatenate with existing data
                        all_dataframes[company] = pd.concat([all_dataframes[company], df])

                    # Create new figure from trend_children
                    fig = go.Figure(trend_children[j].figure)

                    # Update chart data with new dates
                    for trace in fig.data:
                        if hasattr(trace, 'x'):
                            trace.x = df.index

                    # Configure x-axis to properly display dates
                    fig.update_layout(
                        xaxis=dict(
                            type='date',
                            tickformat='%b %Y',  # Format to display "Jan 2024"
                            dtick='M4',  # Show tick every 4 months
                            tickangle=0,
                            rangeslider=dict(visible=False),
                            gridcolor='rgba(128, 128, 128, 0.1)',
                            showgrid=True,
                            tickfont=dict(size=10)
                        ),
                        xaxis_title="Date",
                        plot_bgcolor='rgba(240, 244, 250, 1)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )

                    # Create new graph with updated figure
                    new_graph = dcc.Graph(
                        figure=fig,
                        config=PLOTLY_CONFIG
                    )
                    children.append(new_graph)

                # Create multi-index DataFrame like in generated_data.csv
        final_df = pd.concat(all_dataframes, axis=1, keys=all_dataframes.keys())
        final_df.columns.names = ['symbol', None]

        # Convert to serializable format
        # Flatten multi-index columns by joining with separator
        final_df.columns = [f"{col[0]}|{col[1]}" for col in final_df.columns]

        # Convert to dictionary with simple format
        json_data = {
            'data': final_df.to_dict(orient='split'),
            'column_names': final_df.columns.tolist()
        }


        # Return the container with the new graphs
        return html.Div(
            children=children,
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '20px',
                'width': '100%',
                'maxHeight': '500px',
                'overflowY': 'auto'
            }
        ), json_data

    except Exception as e:
        print('Error while generating preview:', e)
        return html.Div(), {}



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
    State("new-graph-df", "data"),
    prevent_initial_call=True
)
def export_to_csv(n, graph_data):
    """
    Export all companies data to CSV when the modify button is clicked.
    
    Args:
        n (int): Number of clicks on the modify button
        graph_data (dict): Dictionary containing all companies data in simplified format
        
    Returns:
        dict: No update to the current chart figure if successful, or error message if failed
        
    Raises:
        PreventUpdate: If graph_data is empty
    """
    if not graph_data:
        raise PreventUpdate

    try:
        # Reconstruire le DataFrame à partir des données
        df = pd.DataFrame(**graph_data['data'])
        
        # Recréer le multi-index pour les colonnes
        df.columns = pd.MultiIndex.from_tuples(
            [tuple(col.split('|')) for col in graph_data['column_names']],
            names=['symbol', None]
        )
        
        # Pour chaque symbole dans le DataFrame, exporter ses données
        symbols = df.columns.get_level_values('symbol').unique()
        for symbol in symbols:
            symbol_data = df[symbol]
            export_generated_data(symbol_data, symbol)
        
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
        else:
            return go.Figure()
    except Exception as e:
        return go.Figure(layout={"title": f"Erreur : {e}"})

    # Déterminer la longueur utile
    pattern_len = 2 if pattern_name in ["bullish_engulfing", "bearish_engulfing"] else 1
    if pattern_name == "hammer" or pattern_name == "shooting_star":
        pattern_len = 1
    elif pattern_name == "double_top":
        pattern_len = 5
    elif pattern_name == "head_and_shoulders":
        pattern_len = 6

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
        )
    ])
    fig.update_layout(
        xaxis_title="Jour",
        yaxis_title="Prix",
        title=f"Aperçu : {pattern_name.replace('_', ' ').title()}",
        xaxis=dict(tickvals=list(range(pattern_len)), ticktext=[f"Jour {i+1}" for i in range(pattern_len)])
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
    if not pattern_name:
        return dmc.Alert("Veuillez sélectionner un pattern.", color="red")
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
    return dmc.Alert("Configuration sauvegardée !", color="green")




