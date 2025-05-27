import json
import os
from random import randint

import dash
import pandas as pd
from dash import callback, Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from pandas import DataFrame

from trade.utils.settings.create_market_data import get_generated_data
from trade.utils.settings.display import display_chart
from trade.defaults import defaults as dlt


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
    timeline_children = args[-1]

    if not dash.ctx.triggered:
        return timeline_children or []
    button_id = dash.ctx.triggered[0]['prop_id'].split('.')[0]
    button_id = json.loads(button_id)["index"]

    add_clicks = len(timeline_children or [])

    # Exemple d'ajout d'éléments dans la timeline
    new_item = html.Div(
[button_id,
         html.Div([
             html.Button('←', id={'type': 'move-left', 'index': add_clicks},style={'color':'white'}, n_clicks=0),
             html.Button('→', id={'type': 'move-right', 'index': add_clicks},style={'color':'white'}, n_clicks=0),
         ], style={'display': 'flex', 'justifyContent': 'space-between','color':'white'}),
        html.Button(
            'Delete',
            id={'type': 'delete-button', 'index': add_clicks},
            n_clicks=0,
            style={
                'color': 'white',
                'position': 'relative',
                'bottom': '5px',
                'right': '5px'
            }
        )
        ],
        style={
            'width': '100px',
            'height': '100px',
            'backgroundColor': 'green' if 'Bull' in button_id else 'red' if 'Bear' in button_id else 'gray',
            'display': 'flex',
            'color':'white',
            'flexDirection': 'column',
            'justifyContent': 'space-between',
            'resize': 'horizontal',
            'overflow': 'auto'
        },
        id=f"item-{add_clicks}",
    )
    timeline_items = timeline_children or []
    timeline_items.append(new_item)
    return timeline_items


@callback(
    Output('chart_new', 'figure',allow_duplicate=True),
    Input('size-store', 'data'),
    prevent_initial_call=True
)
def graph_preview_new(size_data):

    note = {
        "Very Bull" : 3,
        "Medium Bull": 2,
        "Small Bull": 1,
        "Flat": 0,
        "Small Bear": -1,
        "Medium Bear": -2,
        "Very Bear": -3,

    }
    lenght = int()
    for item in size_data:
        lenght += size_data[item]["width"]

    data = {}
    for item in size_data:
        if size_data[item]["width"] == 0:
            continue
        data[item] = size_data[item]
        data[item]["id"] = int(item[5:])
        data[item]["w"] = int(size_data[item]["width"])
        data[item]["note"] = note[size_data[item]["label"]]

    x = list()
    y = list()
    j=0
    for item in data:
        for _ in range(data[item]["w"]):
            x.append(j)
            y.append(data[item]["note"])
            j+=1

    y = from_trends_to_market_value(data=data, x=x, y=y)

    df =  {"x": x, "y": y}
    df = pd.DataFrame(df)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['x'], y=df['y'],mode="lines+markers",name="lines+markers"))
    fig.update_layout(title= "Exemple", xaxis_title= "Temps",yaxis_title= "Valeur")

    return fig



@callback(
    Output('timeline', 'children', allow_duplicate=True),
    Input({'type': 'delete-button', 'index': dash.ALL}, 'n_clicks'),
    State('timeline', 'children'),
    prevent_initial_call=True
)
def delete_smash(delete_clicks, timeline_children):

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


def from_trends_to_market_value(data: dict, x: list, y: list) -> list:

    init: int = 100

    base_volatility: int = 2

    output = [init for _ in range(len(y))]

    for i in range(1, len(output)):
        # Génère un pourcentage de variation en fonction de y[i]
        # y[i] va de -3 à 3
        # On construit un intervalle de pourcentage basé sur y[i] (par exemple entre -2% et +2% si y[i] = 0)
        variation_bounds = (-base_volatility  + y[i] ** 2, base_volatility  + y[i] ** 2)

        # Détermine le signe selon la note (négatif si y[i] < 0, positif sinon)
        sign = -1 if y[i] < 0 else 1

        # Valeur de pourcentage (entre variation_bounds[0] et variation_bounds[1])
        percentage = randint(*variation_bounds) / 1000

        # Applique la variation en pourcentage sur la valeur précédente
        output[i] = output[i - 1] * (1 + sign * percentage)



    return output

def from_market_value_to_TODO(df: DataFrame):

    companies = dlt.companies_list

    start_date = dlt.start_date




