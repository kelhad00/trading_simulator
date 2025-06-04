import json
import os
from random import randint

import dash
import pandas as pd
from dash import callback, Input, Output, State, html, no_update, dcc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from pandas import DataFrame
import numpy as np
import dash_mantine_components as dmc

from trade.utils.market import get_first_timestamp
from trade.utils.settings.create_market_data import get_generated_data, export_generated_data
from trade.utils.settings.display import display_chart
from trade.defaults import defaults as dlt
from trade.utils.graph.candlestick_charts import PLOTLY_CONFIG
from trade.callbacks.settings.charts.modal import generate_new_charts


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
        [button_id,
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
        id=f"item-{add_clicks}",
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
        "Very": 1000,
        "Medium": 500,
        "Small": 250,
        "Flat": 100
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
        
        # Determine trend type and alpha
        intensity = next((level for level in ["Very", "Medium", "Small"] if level in label), "Flat")
        alpha = alpha_map[intensity]
        
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
    for key, value in dlt.companies_list.items():
        if key.startswith('^'):
            companies.append(value['label'])
        else:
            companies.append(key)

    if not companies:
        return html.Div(), {}

    try:
        # Get existing data to get the date range
        existing_df = get_generated_data()
        if existing_df.empty:
            return html.Div(), {}
            
        # Get the date range
        dates = existing_df.index
        
        # Calculer les proportions pour chaque tendance
        total_width = sum(lengths)
        proportions = [length/total_width for length in lengths]
        
        # Diviser les dates selon les proportions
        date_ranges = []
        start_idx = 0
        for prop in proportions:
            end_idx = start_idx + int(prop * len(dates))
            date_ranges.append(dates[start_idx:end_idx])
            start_idx = end_idx
            
        # Générer les graphiques pour chaque tendance
        children = []
        all_dataframes = {}  # Pour stocker les données de toutes les entreprises
        
        for i, (trend, alpha, date_range) in enumerate(zip(trends, alphas, date_ranges)):
            trend_children = []
            dataframes = []
            for company in companies:
                company_children, company_dataframes = generate_new_charts(
                    alpha=alpha,
                    length=len(date_range),
                    start_value=randint(100,1000),
                    radio_trends=[trend],
                    companies=[company]
                )
                if company_children and company_dataframes:
                    trend_children.extend(company_children)
                    dataframes.extend(company_dataframes)
            
            if trend_children and dataframes:
                # Pour chaque graphique, mettre à jour les dates
                for j, df_dict in enumerate(dataframes):
                    df = pd.DataFrame.from_dict(df_dict)
                    date_index = pd.date_range(start=first_timestamp, periods=df.shape[0], freq='D')
                    df.set_index(date_index, inplace=True)
                    
                    # Stocker les données dans le dictionnaire global
                    company = companies[j]
                    if company not in all_dataframes:
                        all_dataframes[company] = df
                    else:
                        # Concaténer avec les données existantes
                        all_dataframes[company] = pd.concat([all_dataframes[company], df])
                    
                    # Mettre à jour le graphique avec les nouvelles dates
                    fig = go.Figure(trend_children[j].figure)
                    
                    # Mettre à jour les données du graphique avec les nouvelles dates
                    for trace in fig.data:
                        if hasattr(trace, 'x'):
                            trace.x = df.index
                    
                    # Configurer l'axe des x pour afficher correctement les dates
                    fig.update_layout(
                        xaxis=dict(
                            type='date',
                            tickformat='%b %Y',  # Format pour afficher "Jan 2024"
                            dtick='M4',  # Affiche une graduation tous les 4 mois
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
                    
                    # Créer un nouveau graphique avec les dates mises à jour
                    new_graph = dcc.Graph(
                        figure=fig,
                        config=PLOTLY_CONFIG
                    )
                    children.append(new_graph)

        if not children:
            return html.Div(), {}
            
        # Créer un DataFrame multi-index comme dans generated_data.csv
        final_df = pd.concat(all_dataframes, axis=1, keys=all_dataframes.keys())
        final_df.columns.names = ['symbol', None]
        
        # Convertir en format sérialisable
        # Aplatir les colonnes multi-index en les joignant avec un séparateur
        final_df.columns = [f"{col[0]}|{col[1]}" for col in final_df.columns]
        
        # Convertir en dictionnaire avec un format simple
        json_data = {
            'data': final_df.to_dict(orient='split'),
            'column_names': final_df.columns.tolist()
        }
        
        # Retourner le conteneur avec les graphiques et les données
        return html.Div(
            children=children,
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '20px',
                'width': '100%'
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




