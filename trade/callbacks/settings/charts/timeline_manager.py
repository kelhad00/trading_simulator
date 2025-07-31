import json

import dash
import dash_mantine_components as dmc
from dash import callback, Input, Output, State, html, ALL, page_registry
from dash.exceptions import PreventUpdate
from trade.locales import translations as tls


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
            'width': '200px',
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

@callback(
    Output('timeline', 'children', allow_duplicate=True),
    Input({'type': 'add-button', 'index': dash.ALL, 'pattern_type': ALL}, 'n_clicks'),
    State('timeline', 'children'),
    prevent_initial_call=True
)
def add_item_to_timeline(*args):
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
        label_txt = label_txt[len("Ajouter "):]
    elif label_txt.startswith("Add "):
        label_txt = label_txt[len("Add "):]
    color = 'green' if 'Bull' in label else 'red' if 'Bear' in label else 'gray'
    add_clicks = len(timeline_children or [])
    new_item = html.Div(
        [
            # Poignée gauche
            html.Div(
                id={'type': 'resize-handle-left', 'index': add_clicks},
                style={
                    "position": "absolute",
                    "top": 0,
                    "left": 0,
                    "width": "6px",
                    "height": "100%",
                    "cursor": "ew-resize",
                    "zIndex": 10,
                    "backgroundColor": "transparent"
                }
            ),
            # Poignée droite
            html.Div(
                id={'type': 'resize-handle-right', 'index': add_clicks},
                style={
                    "position": "absolute",
                    "top": 0,
                    "right": 0,
                    "width": "6px",
                    "height": "100%",
                    "cursor": "ew-resize",
                    "zIndex": 10,
                    "backgroundColor": "transparent"
                }
            ),
            # Contenu
            html.Div([
                html.Strong(label_txt),
                html.Div(type_label, style={
                    "fontSize": "0.8em",
                    "fontWeight": 400,
                    "marginTop": "2px"
                }),
            ]),
            # Flèche de déplacement
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
            #Button suppression
            dmc.Button(
                "Supprimer" if lang == "fr" else "Delete",
                id={'type': 'delete-button', 'index': add_clicks},
                color="red",
                size="xs",
                variant="filled",
                n_clicks=0,
                style={
                    'position': 'relative',
                    'width': '100%',
                    'marginTop': '4px',
                }
            ),
            # Bouton conditionnel "Edit"
            *([
                  dmc.Button(
                      "Config",
                      id={'type': 'open-modal-config-pattern', 'index': add_clicks},
                      color="blue",
                      size="xs",
                      variant="filled",
                      n_clicks=0,
                      style={
                          'width': '100%',
                          'marginBottom': '4px'
                      }
                  ),
                  dmc.Modal(
                      id={'type': 'modal-config-pattern', 'index': add_clicks},
                      opened=False,
                      title="Configuration des patterns" if lang == "fr" else "Configuration of patterns",
                      children="""TODO
                                Liste des patterns 'autoriser'
                                Quantité par patterns
                                """,
                  )
              ] if pattern_type == "with" else []),
        ],
        style={
            'width': '120px',
            'height': '200px',
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
            'overflow': 'auto',
            'userSelect': 'none',
            'position': 'relative'  # nécessaire pour que les poignées soient positionnées correctement
        },
        id=f"item-{add_clicks}-{label}",
    )

    timeline_items = timeline_children or []
    timeline_items.append(new_item)
    return timeline_items


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
        arrow_div = item["props"]["children"][3]
        left_button = arrow_div["props"]["children"][0]
        right_button = arrow_div["props"]["children"][1]
        delete_button = item["props"]["children"][4]
        if 5 < len(item["props"]["children"]):
            open_modal_button = item["props"]["children"][5]
            open_modal_button["props"]["id"]["index"] = i
            open_modal_config = item["props"]["children"][6]
            open_modal_config["props"]["id"]["index"] = i

        left_button["props"]["id"]["index"] = i
        right_button["props"]["id"]["index"] = i
        delete_button["props"]["id"]["index"] = i

    return timeline

@callback(
    Output('timeline', 'children', allow_duplicate=True),
    Input('add-pattern-button', 'n_clicks'),
    State('pattern-selector', 'value'),
    State('timeline', 'children'),
    State({'type': 'pattern-section', 'pattern_type': ALL}, 'id'),
    prevent_initial_call=True
)
def add_pattern_block(n_clicks, selected_pattern, timeline_children, section_ids):
    if not selected_pattern:
        raise PreventUpdate
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

    new_item = make_timeline_block(label, color, index, pattern_id=selected_pattern, pattern_type="dont")
    timeline_items.append(new_item)
    return timeline_items

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
    for i, item in enumerate(timeline_items):
        item["props"]["id"] = f"item-{i}"
        arrow_div = item["props"]["children"][3]
        left_button = arrow_div["props"]["children"][0]
        right_button = arrow_div["props"]["children"][1]
        delete_button = item["props"]["children"][4]
        if 5 < len(item["props"]["children"]):
            open_modal_button = item["props"]["children"][5]
            open_modal_button["props"]["id"]["index"] = i

        left_button["props"]["id"]["index"] = i
        right_button["props"]["id"]["index"] = i
        delete_button["props"]["id"]["index"] = i
    # Supprimer l'entrée correspondante dans size_data (en respectant l'ordre)
    if size_data and isinstance(size_data, dict):
        keys = list(size_data.keys())
        if 0 <= index_to_delete < len(keys):
            del size_data[keys[index_to_delete]]

    return timeline_items, size_data

@callback(
    Output({'type': 'modal-config-pattern', 'index': dash.ALL}, 'opened'),
    Input({'type': 'open-modal-config-pattern', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def toggle_modal(open_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    triggered_id_dict = json.loads(triggered_id)
    triggered_index = triggered_id_dict['index']

    # Pour chaque modal on va ouvrir la bonne, fermer les autres
    opened_list = []
    for modal_index in range(len(open_clicks)):
        opened_list.append(modal_index == triggered_index)

    return opened_list