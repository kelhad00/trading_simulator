from dash import Dash, html, dcc, dash_table, Output, Input, State, Patch, ALL
import os
from datetime import datetime
import pandas as pd
import numpy as np

from candlestick_charts import create_next_graph, PLOTLY_CONFIG

# Constants
UPDATE_TIME = 5*1000 # in milliseconds
MAX_INV_MONEY=100000
COMP = [ # List of stocks to download
    "MC.PA",  "TTE.PA", "SAN.PA", "OR.PA",  "SU.PA", \
    "AI.PA",  "AIR.PA", "BNP.PA", "DG.PA",  "CS.PA", \
    "RMS.PA", "EL.PA",  "SAF.PA", "KER.PA", "RI.PA", \
    "STLAM.MI",  "BN.PA",  "STMPA.PA",  "CAP.PA", "SGO.PA"
]
NEWS_DATA = pd.DataFrame({
	"date": ["05/05/2023 10:03", "05/05/2023 11:27","05/05/2023 11:45","05/05/2023 11:45","05/05/2023 11:45"],
	"titre": ['Tesla bought Twitter','CAC40 is falling','News','News 23', 'News NEWS']
})


# Initialize Dash app
app = Dash(__name__)


# Layout of the app
app.layout = html.Div([

	# Global variables
	dcc.Store(id = 'market-timestamp-value', data = ''), # Store timestamp value in the browser
	dcc.Store(id = 'market-dataframe'),                  # Store market data in the browserz
	dcc.Store(id = 'price-dataframe'),                  # Store market data in the browserz
	dcc.Store(id = 'request-list', data = []),
	dcc.Store(id = 'portfolio_info', data = {
		'Stock':COMP,
		'Shares': np.zeros(len(COMP)),
		'Total': np.zeros(len(COMP))
	}),

	# Periodic updater
	dcc.Interval(
		id='periodic-updater',
		interval=UPDATE_TIME, # in milliseconds
	),

	# Upper part
	html.Div([
		# Portfolio
		html.Div(children=[
			html.H2(children='Portfolio'),
			html.Div(id='portfolio-table-container'),
			html.P(id='portfolio-total-price')
		], style={'padding': 10, 'flex': 2}),

		# Company graph
		html.Div(children=[
			dcc.Dropdown(COMP, COMP[0], id='company-selector'),
			dcc.Graph(
				id='company-graph',
				figure={'layout': {'height': 300}},
				config = PLOTLY_CONFIG,
				style={'padding': 30}
			)
		], style={'padding-top': 30, 'flex': 3})
	], style={'display': 'flex', 'flex-direction': 'row', 'height': '50vh'}),

	# Lower part
	html.Div([
		# News
		html.Div(children=[
			html.H2(children='Market News'),
			dash_table.DataTable(
				id='news-table',
				data=NEWS_DATA.to_dict('records'),
			)
		], style={'padding': 10, 'flex': 1}),

		# Requests
		html.Div(children=[
			html.H2('Make A Request'),

			html.Label('Prix', htmlFor='price-input'),
			dcc.Input(id='price-input',value='(€)', type='number',min=0),

			html.Label('Parts', htmlFor='nbr-part-input'),
			dcc.Input(id='nbr-part-input',value='(€)', type='number',min=0, max=10, step=1),

			html.Label('Actions', htmlFor='action-input'),
			dcc.RadioItems(['Acheter', 'Vendre'], "Acheter",id="action-input"),

			html.Button("Submit",id='submit-button', n_clicks=0,style={"color":"black"})
		], style={'padding': 10, 'flex': 1, 'display': 'flex', 'flex-direction': 'column', 'margin-left': '5%', 'margin-right': '5%'}),

		html.Div(children=[
			html.H2('Request List'),
			html.Table([
				html.Thead(
					html.Tr(['Prix ','Parts ','Comp ','Actions '])
				)
			],id="title-table"),
			html.Div(id="request-container"),
			html.Button("Clear",id="clear-done-btn")
		], style={'padding': 10, 'flex': 1})

	], style={'display': 'flex', 'flex-direction': 'row', 'height': '50vh'})

])


# Callbacks
@app.callback(
    Output("market-dataframe", "data"),
	Output("price-dataframe", "data"),
    Input('company-selector', 'value'),
	State("price-dataframe", "data"),
)
def import_market_data(company_id, price_list):
	""" Import market data from CSV file
	"""
	df = pd.read_csv('market_data.csv', index_col=0, header=[0,1])

	if not price_list: # if the dataframe has not been loaded yet
		price_list = df.xs('Close', axis=1, level=1)
		price_list = price_list.to_dict()

	return df[company_id].to_dict(), price_list


@app.callback(
	Output('company-graph', 'figure'),          # new graph
	Output('market-timestamp-value', 'data'),   # new timestamp
	Input('periodic-updater', 'n_intervals'), 	# periodicly updated
	Input('market-dataframe', 'data'),          # new company is selected
	State('market-timestamp-value', 'data') 	# Last timestamp
)
def update_graph(n, df, timestamp, range=80):
	""" Update the graph with the latest market data
		Periodicly updated or when the user selects a new company
	"""
	dftmp = pd.DataFrame.from_dict(df)
	fig, timestamp = create_next_graph(
        # pd.DataFrame.from_records(df),
		dftmp,
        timestamp,
        range
    )
	fig.update_layout(
        margin_t = 0,
        margin_b = 0,
        height = 300,
    )
	return fig, timestamp


@app.callback(
	Output('portfolio-table-container', 'children'),
	Input('portfolio_info', 'data')
)
def generate_portfolio_table(stocks_info):
	""" Update the portfolio table with the latest user's portfolio information
	"""
	df = pd.DataFrame.from_dict(stocks_info)
	column_size = 10
	stock_size = len(df)
	return html.Div([
		html.Table([
			html.Thead([
				html.Tr([
					html.Th(
						col,
						style={'padding-right': 50,'border-color': '#d3d3d3', 'border-style': 'solid','border-width': '1px'}
					) for col in  df.columns
				], style = {'background-color': '#fafafa'})
			]),
			html.Tbody([
				html.Tr([
					html.Td(
						df.iloc[i][col],
						style={'border-color': '#d3d3d3', 'border-style': 'solid', 'border-width': '1px'}
					) for col in df.columns
				]) for i in range(j,column_size + j)
			])
		]) for j in range(0, stock_size, column_size)
    ], style={'display': 'flex', 'flex-direction': 'row'})


@app.callback(
	Output('portfolio-total-price', 'children'),
	Input('portfolio_info', 'data')
)
def calcul_prix_tot_inv(stock_info):
	""" Update the portfolio total price
	"""
	totals = pd.DataFrame.from_dict(stock_info)['Total']
	return ['Votre investissement total : ', totals.sum(),' eur.']


@app.callback(
    Output(component_id="request-container", component_property="children", allow_duplicate=True),
	Output("request-list", "data", allow_duplicate=True),
    Input("submit-button", "n_clicks"),
    [State("price-input", "value"),State("nbr-part-input", "value"),State("company-selector", "value"),State("action-input","value"),State("request-list", "data")],
    prevent_initial_call=True,
)
def ajouter_requetes(button_clicked,prix,part,companie,action,req):
	patched_list = Patch()

	def generate_line(value):
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
			]
		)

	value = [prix,part,companie,action]
	req.append(value)
	patched_list.append(generate_line(value))

	return patched_list, req


@app.callback(
    Output("request-container", "children", allow_duplicate=True),
    Output("request-list", "data"),
	Input("periodic-updater", "n_intervals"),
    State("request-list", "data"),
	State('market-dataframe','data'),
	State('market-timestamp-value','data'),
	prevent_initial_call=True
)
def test_prix(n, request_list, df, timestamp):
	patched_list = Patch()
	list_price = pd.DataFrame.from_dict(df)['Close'][timestamp]
	for i,rq in request_list:
		stock_price = list_price[rq[2]]
		if rq[3] == 'Acheter' and rq[0] <= stock_price:
			request_list.remove(rq)
			patched_list.remove(rq)
			#fonction acheter
		elif rq[3] == 'Vendre' and rq[0] >= stock_price:
			request_list.remove(rq)
			patched_list.remove(rq)
			#fonction vendre
	return patched_list,request_list


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


if __name__ == '__main__':
    app.run_server(debug=True) #TODO: change to False when deploying