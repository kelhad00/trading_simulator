import json
import os

import dash
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import callback, Input, Output, State, page_registry, ALL
from dash import html

from trade.callbacks.settings.charts.patterns_generator import insert_bullish_engulfing, insert_bearish_engulfing, \
    insert_hammer, insert_shooting_star, insert_double_top, insert_head_and_shoulders, insert_double_bottom, \
    insert_inverse_head_and_shoulders
from trade.defaults import defaults as dlt
from trade.locales import translations as tls

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
        {"name": tls[page_registry.get('lang', 'fr')]["settings"]["charts"]["subtitles"]["duration"], "type": "number",
         "min": 5, "max": 100, "step": 1, "value": 6},
    ],
    "head_and_shoulders": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": tls[page_registry.get('lang', 'fr')]["settings"]["charts"]["subtitles"]["duration"], "type": "number",
         "min": 5, "max": 100, "step": 1, "value": 6},
    ],
    "double_bottom": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": tls[page_registry.get('lang', 'fr')]["settings"]["charts"]["subtitles"]["duration"], "type": "number",
         "min": 5, "max": 100, "step": 1, "value": 6},
    ],
    "inverse_head_and_shoulders": [
        {"name": "Amplitude", "type": "number", "min": 0.5, "max": 2.0, "step": 0.01, "value": 1.0},
        {"name": tls[page_registry.get('lang', 'fr')]["settings"]["charts"]["subtitles"]["duration"], "type": "number",
         "min": 5, "max": 100, "step": 1, "value": 6},
    ],
}


@callback(
    Output("pattern-preview-graph", "figure"),
    Input("pattern-select", "value"),
    Input({"type": "pattern-param", "name": ALL}, "value"),
    State({"type": "pattern-param", "name": ALL}, "id"),
)
def update_pattern_preview(pattern_name, param_values, param_ids):
    """Render a live preview for the selected pattern with given parameters.

    Args:
        pattern_name (str): Selected pattern key.
        param_values (list): Parameter values from sliders.
        param_ids (list): Parameter metadata including names.

    Returns:
        go.Figure: Preview figure or empty figure when not applicable.
    """
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
    n = params.get("duree", 6)  # nombre de jours max pour les patterns
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
        return go.Figure(layout={"title": f"Loading...."})

    pattern_len = n

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
        xaxis=dict(tickvals=list(range(pattern_len)), ticktext=[f"{day_label} {i + 1}" for i in range(pattern_len)])
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
    """Persist current pattern parameters into `pattern_configs.json`.

    Returns a translated success/error alert component.
    """
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


@callback(
    Output("pattern-params-container", "children"),
    Input("pattern-select", "value"),
    Input("reset-pattern-config-btn", "n_clicks"),
    State({"type": "pattern-param", "name": ALL}, "value"),
    State({"type": "pattern-param", "name": ALL}, "id"),
    prevent_initial_call=True
)
def update_pattern_params(pattern_name, reset_clicks, current_values, current_ids):
    """Render parameter sliders for a pattern, loading/saving defaults as needed."""
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
        value_map = {id_["name"]: val for id_, val in zip(current_ids, current_values)} if current_ids else {
            param["name"]: param["value"] for param in params}
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
    Output({"type": "pattern-param-value", "name": ALL}, "children"),
    Input({"type": "pattern-param", "name": ALL}, "value"),
    State({"type": "pattern-param", "name": ALL}, "id"),
)
def update_pattern_param_values(values, ids):
    """Return textual values for each parameter slider to display alongside."""
    return [str(v) for v in values]
