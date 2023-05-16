from dash import Dash, dcc, html, Input, Output, State, Patch,ALL
import plotly.express as px
import pandas as pd

#mendatory
app = Dash(__name__)

inv_start=100000
list_comp= ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "NVDA", "PEP", "COST"]
prix_tot=[]
num_part=[]
data=[]
prix_actu=[10,10,10,10,10,10,10,10,10]


for c in list_comp:
    line=[c,0,0]
    data.append(line)

@app.callback(
    Output(component_id="request-container", component_property="children", allow_duplicate=True),
    Input("submit-button", "n_clicks"),
    [State("price-input", "value"),State("nbr-part-input", "value"),State("companie-input", "value"),State("action-input","value")],
    prevent_initial_call=True,
)
def ajouter_requetes(button_clicked,prix,part,companie,action):
    patched_list = Patch()

    def generate_line():
        value=[prix,part,companie,action]
        return html.Div(
            [
                html.Div(
                    str(value),
                    id={"index": button_clicked, "type": "output-str"},
                    style={"display": "inline", "margin": "10px"},
                ),
                dcc.Checklist(
                    options=[{"label": "", "value": "done"}],
                    id={"index": button_clicked, "type": "done"},
                    style={"display": "inline"},
                    labelStyle={"display": "inline"},
                ), 
            ],
        )
    patched_list.append(generate_line())
    return patched_list

# Callback to delete items marked as done
@app.callback(
    Output("request-container", "children", allow_duplicate=True),
    Input("clear-done-btn", "n_clicks"),
    State({"index": ALL, "type": "done"}, "value"),
    prevent_initial_call=True,
)
def delete_items(n_clicks, state):
    patched_list = Patch()
    values_to_remove = []
    for i, val in enumerate(state):
        if val:
            values_to_remove.insert(0, i)
    for v in values_to_remove:
        del patched_list[v]
    return patched_list


#create the starting portfolio
def generate_table(dataframe):
    return html.Table([
        html.Thead(
            html.Th(['Companie ','Parts ','Prix '])
        ),
        html.Tbody([
            html.Tr([
                html.Td(i) for i in ligne
                ])for ligne in dataframe
            ])
    ],style={"text-align":"center","table-layout":'fixed',"border": "1px solid black"})


#Test prix_actu with prices in request
@app.callback(
    Output("request-container", "children", allow_duplicate=True),
    Input("request-container",'children'),
    State({"index": ALL, "type": "output-str"}, "value"),
    prevent_initial_call=True,
)
def test_price(stri,state):   
    patched_list = Patch()
    list_to_remove=[]
    for i,val in enumerate(state):
        if i==1:
            list_to_remove.insert(0,i)
        print(i,val)
    for v in list_to_remove:
        del patched_list[v]
    return patched_list





#APP LAYOUT
app.layout = html.Div([
    html.Div([

    html.H4('Request List',style={"font-size": "25px",'color': '#DEB887'}),
    html.Table([
            html.Thead(
                html.Tr(['Prix ','Parts ','Comp ','Actions '])
            )
        ],id="title-table"),
    html.Div(id="request-container"),
    html.Button("Clear",id="clear-done-btn")
    ]),
    
    html.Div([

    html.Br(),
    html.H4('Make A Request',style={"font-size": "25px"}),
    html.Label('Prix'),
    dcc.Input(id='price-input',value='(€)', type='number',min=0),
    
    html.Br(),
    html.Label('Parts'),
    dcc.Input(id='nbr-part-input',value='(€)', type='number',min=0, max=10, step=1),
    

    html.Br(),
    html.Label('Companie'),
    dcc.Dropdown(["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "NVDA", "PEP", "COST"],id='companie-input',value='AAPL'),
    
    html.Label('Actions'),
    dcc.RadioItems(['Acheter', 'Vendre'], "Acheter",id="action-input"),
    
    html.Br(),
    html.Button("Submit",id='submit-button', n_clicks=0,style={"color":"black"})
    ]),

    html.Div([
        html.H4("Portfolio",style={"font-size": "25px"}),
        generate_table(data)
        ])

])

    
#not mendatory
if __name__ == '__main__':
    app.run_server(debug=True)