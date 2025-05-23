import json
import os

import dash
from dash import callback, Input, Output, State, html
from dash.exceptions import PreventUpdate

from trade.app import app
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
[button_id[4:],
         html.Div([
             html.Button('←', id={'type': 'move-left', 'index': add_clicks}, n_clicks=0),
             html.Button('→', id={'type': 'move-right', 'index': add_clicks}, n_clicks=0),
         ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        html.Button(
            'Delete',
            id={'type': 'delete-button', 'index': add_clicks},
            n_clicks=0,
            style={
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
    Output('json', 'children', allow_duplicate=True),
    Input('size-store', 'data'),
    prevent_initial_call=True
)
def refresh_smash(size_data):

    keys_to_remove = [key for key, value in size_data.items() if value["width"] == 0]

    for key in keys_to_remove:
        del size_data[key]

    if not dash.callback_context.triggered:
        return "No action yet."

    res = 0

    for item in size_data:
        width = size_data[item]["width"]
        res += width

    return f"Global lenght {res}"


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
        print(item)
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
    # Re-synchroniser les index dans les IDs
    for i, item in enumerate(timeline):
        item["props"]["id"] = f"item-{i}"
        item["props"]["children"][1]["props"]["children"][0]["props"]["id"]["index"] = i  # ←
        item["props"]["children"][1]["props"]["children"][1]["props"]["id"]["index"] = i  # →
        item["props"]["children"][2]["props"]["id"]["index"] = i  # Delete

    return timeline



app.clientside_callback(
    """
    function(n_clicks) {
        if (!window.itemSizesInitialized) {
            window.itemSizes = {};
            window.itemSizesInitialized = true;

            const observer = new ResizeObserver(entries => {
                entries.forEach(entry => {
                    const id = entry.target.id;
                    if (id && id.startsWith("item-")) {
                        window.itemSizes[id] = {
                            width: entry.contentRect.width,
                            height: entry.contentRect.height
                        };
                    }
                });
            });

            function observeExisting() {
                document.querySelectorAll('[id^="item-"]').forEach(el => observer.observe(el));
            }

            observeExisting();

            const timeline = document.getElementById("timeline");
            if (timeline) {
                const mutationObserver = new MutationObserver(mutations => {
                    mutations.forEach(mutation => {
                        mutation.addedNodes.forEach(node => {
                            if (node.nodeType === 1 && node.id && node.id.startsWith("item-")) {
                                observer.observe(node);
                            }
                        });
                        mutation.removedNodes.forEach(node => {
                            if (node.nodeType === 1 && node.id && node.id.startsWith("item-")) {
                                delete window.itemSizes[node.id];
                            }
                        });
                    });
                });
                mutationObserver.observe(timeline, { childList: true, subtree: false });
            }
        }
        return window.itemSizes;
    }
    """,
    Output("size-store", "data"),
    Input("refresh-button", "n_clicks")
)
