import json

import dash
import dash_mantine_components as dmc
from dash import callback, Input, Output, State, html, ALL, page_registry, dcc
from dash.exceptions import PreventUpdate
from trade.locales import translations as tls
from trade.components.radio import radio
from trade.components.modal import modal

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
            # Flèche de déplacement
            html.Div([
                dmc.Button(
                    "←",
                    id={'type': 'move-left', 'index': index},
                    color="dark",
                    size="xs",
                    variant="filled",
                    n_clicks=0,
                    style={'minWidth': '30px'}
                ),
                dmc.Button(
                    "→",
                    id={'type': 'move-right', 'index': index},
                    color="dark",
                    size="xs",
                    variant="filled",
                    n_clicks=0,
                    style={'minWidth': '30px'}
                ),
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '8px', 'padding': '8px'}),
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
            # Bouton conditionnel "Edit"
            *([
                  dmc.Button(
                      "Configuration des patterns" if lang == "fr" else "Configuration of patterns",
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
                  modal(id= {'type': 'modal-config-pattern', 'index': add_clicks},
                        title="Configuration des patterns" if lang == "fr" else "Configuration of patterns",
                        children=[])
              ] if pattern_type == "with" else []),
            #Button suppression
            dmc.Button(
                "Supprimer" if lang == "fr" else "Delete",
                id={'type': 'delete-button', 'index': add_clicks},
                color="red",
                size="xs",
                variant="filled",
                n_clicks=0,
                style={
                    'width': '100%',
                    'marginTop': '4px',
                }
            ),
        ],
        style={
            'width': '200px',
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
    Output('special-pattern-config', 'data', allow_duplicate=True),
    Input({'type': 'move-left', 'index': dash.ALL}, 'n_clicks'),
    Input({'type': 'move-right', 'index': dash.ALL}, 'n_clicks'),
    State('timeline', 'children'),
    State('special-pattern-config', 'data'),
    prevent_initial_call=True
)
def move_item(left_clicks, right_clicks, timeline_children, data):
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
        return timeline_children or [], data

    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    direction = 'left' if 'move-left' in ctx.triggered[0]['prop_id'] else 'right'
    index = button_id['index']

    if not (0 <= index < len(timeline_children)):
        return timeline_children, data

    timeline = timeline_children[:]
    if direction == 'left' and index > 0:
        timeline[index - 1], timeline[index] = timeline[index], timeline[index - 1]
    elif direction == 'right' and index < len(timeline) - 1:
        timeline[index + 1], timeline[index] = timeline[index], timeline[index + 1]

    for i, item in enumerate(timeline):
        item["props"]["id"] = f"item-{i}"
        if len(item["props"]["children"]) <3:
            arrow_div = item["props"]["children"][1]
            left_button = arrow_div["props"]["children"][0]
            right_button = arrow_div["props"]["children"][1]
            delete_button = item["props"]["children"][2]
        if len(item["props"]["children"]) > 3:
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
    data_copy = {}

    for old_index_str, value in data.items():
        old_index = int(old_index_str)

        if direction == 'left':
            if old_index == index:
                # Celui qui a été déplacé à gauche
                data_copy[index - 1] = value
            elif old_index == index - 1:
                # Celui qui était à gauche et se fait décaler à droite
                data_copy[index] = value
            else:
                data_copy[old_index] = value

        elif direction == 'right':
            if old_index == index:
                # Celui qui a été déplacé à droite
                data_copy[index + 1] = value
            elif old_index == index + 1:
                # Celui qui était à droite et se fait décaler à gauche
                data_copy[index] = value
            else:
                data_copy[old_index] = value

    return timeline, data_copy

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
    Output('special-pattern-config', 'data', allow_duplicate=True),
    Input({'type': 'delete-button', 'index': dash.ALL}, 'n_clicks'),
    State('timeline', 'children'),
    State('size-store', 'data'),
    State('special-pattern-config', 'data'),
    prevent_initial_call=True
)
def delete_smash(delete_clicks, timeline_children, size_data, data):
    """
    Delete a timeline item based on button clicks and synchronise with size_data.
    Args:
        delete_clicks (list): List of click counts for delete buttons
        timeline_children (list): Current list of timeline items
        size_data (dict): Current size_data
        data (dict): Current special-pattern-config
    """
    button_id = dash.ctx.triggered[0]['prop_id'].split('.')[0]
    index_to_delete = eval(button_id)['index']

    if (not dash.ctx.triggered) or sum(delete_clicks) == 0:
        return timeline_children or [], size_data, data
    # Supprimer l'élément correspondant dans la timeline
    timeline_items = timeline_children or []
    timeline_items.pop(index_to_delete)
    for i, item in enumerate(timeline_items):
        item["props"]["id"] = f"item-{i}"
        arrow_div = item["props"]["children"][3]
        left_button = arrow_div["props"]["children"][0]
        right_button = arrow_div["props"]["children"][1]
        if 5 < len(item["props"]["children"]):
            open_modal_button = item["props"]["children"][4]
            open_modal_button["props"]["id"]["index"] = i
            delete_button = item["props"]["children"][5]
        else:
            delete_button = item["props"]["children"][4]

        left_button["props"]["id"]["index"] = i
        right_button["props"]["id"]["index"] = i
        delete_button["props"]["id"]["index"] = i
    # Supprimer l'entrée correspondante dans size_data (en respectant l'ordre)
    if size_data and isinstance(size_data, dict):
        keys = list(size_data.keys())
        if 0 <= index_to_delete < len(keys):
            del size_data[keys[index_to_delete]]
    data_copy = {}
    for key in data:
        if int(key) > index_to_delete:
            data_copy[int(key)-1] = data[key]
        elif int(key) < index_to_delete:
            data_copy[int(key)] = data[key]
        elif int(key) == index_to_delete:
            pass

    return timeline_items, size_data, data_copy

@callback(
    Output({'type': 'modal-config-pattern', 'index': dash.ALL}, 'opened', allow_duplicate=True),
    Output({'type': 'modal-config-pattern', 'index': dash.ALL}, 'children', allow_duplicate=True),
    Input({'type': 'open-modal-config-pattern', 'index': dash.ALL}, 'n_clicks'),
    State('timeline', 'children'),
    State('size-store', 'data'),
    prevent_initial_call=True
)
def open_dynamic_modal(open_clicks, timeline ,size_data):
    triggered = dash.ctx.triggered_id
    if not triggered or not isinstance(triggered, dict):
        raise dash.exceptions.PreventUpdate

    index = triggered['index']

    pattern_indices = {}

    for item in timeline:
        children = item["props"]["children"]
        for comp in children:
            if isinstance(comp, dict) and "props" in comp:
                comp_id = comp["props"].get("id", {})
                if isinstance(comp_id, dict) and comp_id.get("type") == "open-modal-config-pattern":
                    idx = comp_id.get("index")
                    pattern_indices[idx] = False
                    break

    opened_list = [False] * len(open_clicks)
    children_list = [dash.no_update] * len(open_clicks)

    trend = timeline[index]["props"]['children'][2]['props']['children'][0]['props']['children']

    content = modal_config_pattern(trend=trend, index=index)

    i=0
    for key in pattern_indices:
        if int(key) == index:
            break
        else:
            i+=1

    opened_list[i] = True
    children_list[i] = content


    return opened_list, children_list

@callback(
    Output('form-output', 'children'),
    Input('form-choice', 'value'),
    State('form-info', 'data'),
    State("special-pattern-config", "data"),
)
def render_form(selected_form, form_info,data_pattern):
    trend = form_info['trend']
    index = form_info['index']

    if str(index) in data_pattern.keys():
        lst = data_pattern[str(index)]
    else:
        lst = []

    if selected_form == 'type':
        return html.Form([
            html.H2("Choix des patterns possibles",
                    style={'fontWeight': 'bold', 'fontSize': '18px'}),
            checkbox_group_from_list(
                bull_pattern if "Bull" in trend else bear_pattern,
                id="form_checkbox",
                label="",
                lst= lst
            ),
            html.Br(),
            dmc.Button("Valider", id="submit-pattern-config-type", n_clicks=0, type="button", color="dark", size="md"),
        ])

    elif selected_form == 'type_count':
        pattern_list = bull_pattern if "Bull" in trend else bear_pattern

        # Récupération des patterns déjà sélectionnés (avec ou sans quantités)
        selected = data_pattern.get(str(index), {})

        return html.Form([
            html.H2("Choix des patterns possibles et de leur quantité",
                    style={'fontWeight': 'bold', 'fontSize': '18px'}),
            html.Div([
                html.Div([
                    dmc.Checkbox(
                        id={'type': 'pattern-checkbox', 'index': pattern},
                        label=tls[page_registry['lang']]["settings"]["charts"]["patterns_names"][pattern],
                        value=pattern,
                        color="dark",
                        checked=pattern in selected,
                    ),
                    dmc.NumberInput(
                        id={'type': 'pattern-count', 'index': pattern},
                        value=selected.get(pattern, 1),
                        min=1,
                        max=10,
                        step=1,
                        size="xs",
                        style={"marginLeft": "10px", "width": "80px"},
                    )
                ],
                    style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "10px"})
                for pattern in pattern_list
            ]),
            html.Br(),
            dmc.Button("Valider", id="submit-pattern-config-type-count", n_clicks=0, type="button", color="dark",
                       size="md"),
        ])

    return html.Div()

def checkbox_group_from_list(items, id="my-checkboxes", label="Choix", lst= []):
    lang =  page_registry['lang']
    tl = tls[lang]["settings"]["charts"]
    return dmc.CheckboxGroup(
        id=id,
        label=label,
        value=lst,
        orientation="vertical",
        children=[dmc.Checkbox(label=tl["patterns_names"][item], value=item, color="dark") for item in items]
    )

def modal_config_pattern(trend,index):
    if "Small" in trend or "Medium" in trend or "Large" in trend:
        title = "Item n° "+str(index+1)+" : "+str(trend)
    else:
        title = "Elément n° "+str(index+1)+" : "+str(trend)
    content = html.Div([
        html.H2(title),
        html.Br(),
        dcc.Store(id="form-info", data={"trend": trend, "index": index}),
        # Radios
        html.Div([
            radio(
                options=[
                    ("type", "Choix des patterns possibles"),
                    ("type_count", "Choix des patterns possibles et de leur quantité")
                ],
                label="Sélection du formulaire",
                id="form-choice",
                value="type"
            )
        ], style={'marginBottom': '20px'}),

        # Zone d'affichage dynamique du formulaire
        html.Div(id='form-output')
    ], style={'padding': '20px'})
    return content

@callback(
    Output('special-pattern-config', 'data', allow_duplicate=True),
    Output({'type': 'modal-config-pattern', 'index': dash.ALL}, 'opened', allow_duplicate=True),
    Input('submit-pattern-config-type', 'n_clicks'),
    State('form_checkbox', 'value'),
    State('form-info', 'data'),
    State("special-pattern-config", "data"),
    State({'type': 'open-modal-config-pattern', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def store_pattern_config(n_clicks, selected_patterns, form_info, data, opened):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    index = form_info['index']
    data[index] = {"name":selected_patterns, "count": [-1]*len(selected_patterns)}
    opened_list = [False] * len(opened)
    return data, opened_list

@callback(
    Output("special-pattern-config", "data", allow_duplicate=True),
    Output({'type': 'modal-config-pattern', 'index': dash.ALL}, 'opened', allow_duplicate=True),
    Input("submit-pattern-config-type-count", "n_clicks"),
    State({'type': 'pattern-checkbox', 'index': ALL}, 'checked'),
    State({'type': 'pattern-checkbox', 'index': ALL}, 'value'),
    State({'type': 'pattern-count', 'index': ALL}, 'value'),
    State("form-info", "data"),
    State("special-pattern-config", "data"),
    State({'type': 'open-modal-config-pattern', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_pattern_with_count(n_clicks, checked_list, pattern_ids, count_list, form_info, current_data, opened):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    index = str(form_info['index'])
    name_list = []
    count_values = []

    for is_checked, pattern_id, count in zip(checked_list, pattern_ids, count_list):
        if is_checked:
            name_list.append(pattern_id)
            count_values.append(count)

    current_data[index] = {
        "name": name_list,
        "count": count_values
    }

    opened_list = [False] * len(opened)
    return current_data, opened_list
