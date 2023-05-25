from dash import Dash, html, dcc, dash_table, Output, Input, State, Patch, ALL, ctx
import os
from datetime import datetime
import pandas as pd
import numpy as np

from Components.candlestick_charts import create_graph, PLOTLY_CONFIG

# Constants
UPDATE_TIME = 8*1000 # in milliseconds
MAX_REQUESTS = 10    # Maximum number of requests
MAX_INV_MONEY=100000 # Initial money
COMP = [ # List of stocks to download
    "MC.PA",  "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA",
    "AIR.PA", "SU.PA", "AI.PA",  "EL.PA",  "BNP.PA",
    "KER.PA", "DG.PA",  "CS.PA", "SAF.PA", "RI.PA",
    "DSY.PA", "STLAM.MI", "BN.PA",  "STMPA.PA",  "ACA.PA"
]


# Initialize Dash app
app = Dash(__name__)


# Layout of the app
app.layout = html.Div([

	# Global variables
	dcc.Store(id = 'nbr-logs', data = 0),                # Number of times the app state has been saved
	dcc.Store(id = 'market-timestamp-value', data = ''), # Store timestamp value in the browser
	dcc.Store(id = 'market-dataframe'),                  # Store market data in the browser
	dcc.Store(id = 'price-dataframe'),                   # Store market data in the browser
	dcc.Store(id = 'news-dataframe'),
	dcc.Store(id = 'news-index', data = 9),              # Display 10 news at the first load (0-9)
	dcc.Store(id = 'cashflow', data = 100000),
	dcc.Store(id = 'request-list', data = []),
	dcc.Store(id = 'liste-skiprows', data=[6,7,8,9,10]),
	dcc.Store(id = 'portfolio_info', data = {c: {'Shares': 0, 'Total': 0} for c in COMP}),

	# Periodic updater
	dcc.Interval(
		id='periodic-updater',
		interval=UPDATE_TIME, # in milliseconds
	),

	#pop-up d'erreur
	dcc.ConfirmDialog(
        id='many-request',
        message='You have too many request ! ',
    ),
	dcc.ConfirmDialog(
        id='form-not-filled',
        message='You haven\'t filled the form correctly ! ',
    ),

	# Upper part
	html.Div([
		# Portfolio
		html.Div(children=[
			html.H2(children='Portfolio'),
			html.Div(id='portfolio-table-container'),
			dcc.Markdown(id='portfolio-total-price')
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
				columns=[{'name': 'Date', 'id': 'Date'}, {'name': 'Title', 'id': 'Title'}],
			)
		], style={'padding': 10, 'flex': 1}),

		# Requests
		html.Div(children=[
			html.H2('Make A Request'),

			html.Label('Prix', htmlFor='price-input'),
			dcc.Input(id='price-input', value=0,type='number',min=0, step=0.1),

			html.Label('Parts', htmlFor='nbr-part-input'),
			dcc.Input(id='nbr-part-input',value=1, type='number',min=1, max=MAX_REQUESTS, step=1),

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
	file_path = os.path.join('Data', 'market_data.csv')
	df = pd.read_csv(file_path, index_col=0, header=[0,1])

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
	# Determining which callback input changed
	if ctx.triggered_id == 'periodic-updater':
		next_graph = True
	else:
		# If the user selected a new company
		# Don’t change the timestamp.
		next_graph = False

	dftmp = pd.DataFrame.from_dict(df)
	fig, timestamp = create_graph(
		dftmp,
        timestamp,
		next_graph,
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
	df = pd.DataFrame.from_dict(stocks_info, orient='index').round(2)
	df['Stock'] = df.index
	column_size = 10
	stock_size = len(df)
	column_names = ['Stock', 'Shares', 'Total']
	return html.Div([
		html.Table([
			html.Thead([
				html.Tr([
					html.Th(
						col,
						style={'padding-right': 50,'border-color': '#d3d3d3', 'border-style': 'solid','border-width': '1px'}
					) for col in column_names
				], style = {'background-color': '#fafafa'})
			]),
			html.Tbody([
				html.Tr([
					html.Td(
						df.iloc[i][col],
						style={'border-color': '#d3d3d3', 'border-style': 'solid', 'border-width': '1px'}
					) for col in column_names
				]) for i in range(j,column_size + j)
			])
		]) for j in range(0, stock_size, column_size)
    ], style={'display': 'flex', 'flex-direction': 'row'})


@app.callback(
	Output('portfolio-total-price', 'children'),
	Input('portfolio_info', 'data'),
	State('cashflow', 'data')
)
def calcul_prix_tot_inv(stock_info, cash):
	""" Update the portfolio total price
	"""
	totals = pd.DataFrame.from_dict(stock_info, orient='index')['Total']
	return [
		'Votre cash disponible : ', round(cash, 2),' eur.\n',
		'Votre investissement total : ', round(cash + totals.sum(), 2),' eur.'
	]


@app.callback(
    Output(component_id="request-container", component_property="children", allow_duplicate=True),
	Output("request-list", "data", allow_duplicate=True),
	Output('many-request', 'displayed'),    # Error message if the user has too many requests
	Output('form-not-filled', 'displayed'), # Error message if the form isn't filled correctly
    Input("submit-button", "n_clicks"),
    State("price-input", "value"),
	State("nbr-part-input", "value"),
	State("company-selector", "value"),
	State("action-input","value"),
	State("request-list", "data"),
    prevent_initial_call=True,
)
def ajouter_requetes(btn,prix,part,companie,action,req):
	patched_list = Patch()

    # If the user has too many requests
	if len(req) == MAX_REQUESTS:
		return patched_list, req, True, False

	# If the form isn't filled correctly
	if prix == 0 and btn != 0:
		return patched_list, req, False, True

	# Add the request to the list
	value = [prix,part,companie,action]
	req.append(value)

	def generate_line(value):
		return html.Div(
			[
				html.Div(
					str(value),
					id={"index": len(req), "type": "output-str"},
					style={"display": "inline", "margin": "10px"},
				),
				dcc.Checklist(
					options=[{"label": "", "value": "done"}],
					id={"index": len(req), "type": "done"},
					style={"display": "inline"},
					labelStyle={"display": "inline"},
				),
			]
		)

	# Show the request list on the interface
	patched_list.append(generate_line(value))

	return patched_list, req, False, False


@app.callback(
    Output("request-container", "children", allow_duplicate=True),
    Output("request-list", "data"),
	Output("portfolio_info", "data"),
	Output("cashflow", "data"),
	Input('market-timestamp-value','data'),
    State("request-list", "data"),
	State('price-dataframe','data'),
	State('portfolio_info','data'),
	State('cashflow','data'),
	prevent_initial_call=True
)
def remove_request(timestamp, request_list, list_price, portfolio_info, cashflow):
	patched_list = Patch() # Get request-container children
	list_price = pd.DataFrame.from_dict(list_price)
	portfolio_info = pd.DataFrame.from_dict(portfolio_info)

	i = 0
	while i < len(request_list):
		req = request_list[i]
		stock_price = list_price[req[2]].loc[timestamp]

		# If the request is completed
		if req[3] == 'Acheter' and req[0] >= stock_price:
			# If the user has enough money
			if req[1] * stock_price < cashflow:
				portfolio_info.loc['Shares', req[2]] += req[1]
				portfolio_info.loc['Total', req[2]] += req[1] * stock_price
				cashflow -= req[1] * stock_price
			# the request is removed, with or without the user having enough money
			del patched_list[i]
			request_list.remove(req)

		# Same as above for the sell request
		elif req[3] == 'Vendre' and req[0] <= stock_price:
			# If the user has enough shares
			if portfolio_info.loc['Shares', req[2]] >= req[1]:
				portfolio_info.loc['Shares', req[2]] -= req[1]
				portfolio_info.loc['Total', req[2]] -= req[1] * stock_price
				cashflow += req[1] * stock_price
			# the request is removed, with or without the user having enough shares
			del patched_list[i]
			request_list.remove(req)

		# If the request is not completed yet, pass to the next one.
		# If the request is completed, the request is removed from the list and
		# the next request is now at the current index.
		else:
			i += 1

	return patched_list,request_list, portfolio_info.to_dict(), cashflow


# Callback to delete items marked as done
@app.callback(
    Output("request-container", "children", allow_duplicate=True),
	Output("request-list", "data", allow_duplicate=True),
    Input("clear-done-btn", "n_clicks"),
    State({"index": ALL, "type": "done"}, "value"),
    prevent_initial_call=True,
)
def delete_items(n_clicks, state):
	patched_list = Patch()
	request_list = Patch()

	values_to_remove = []
	for i, val in enumerate(state):
		if val:
			values_to_remove.insert(0, i)
	for v in values_to_remove:
		del patched_list[v]
		del request_list[v]

	return patched_list, request_list


@app.callback(
	Output('news-index','data'),
	Output('news-dataframe','data'),
	Output('news-table','data'),
	Input('market-timestamp-value','data'),
	State('news-dataframe','data'),
	State('news-index','data'),
)
def update_news_table(timestamp, news_df, idx, range=10):
	""" Display one more news every time the timestamp is updated
		Limit the number of news displayed to the range parameter
	"""
	# If the news dataframe is not loaded yet, load it
	if not news_df:
		file_path = os.path.join('Data', 'news.csv')
		news_df = pd.read_csv(file_path, sep=';', usecols=['Date','Title'])
	else:
		news_df = pd.DataFrame.from_dict(news_df)

	idx += 1
	nl = news_df.iloc[idx - range : idx]

	return idx, news_df.to_dict(), nl.to_dict('records')


@app.callback(
	Output('nbr-logs', 'data'),
	# Data to save
	Input('market-timestamp-value','data'),
	Input('company-selector', 'value'),
	Input('cashflow', 'data'),
	Input('request-list', 'data'),
	Input('portfolio_info', 'data'),
	# number of logs
	State('nbr-logs', 'data')
)
def save_state(timestamp, company_id, cashflow, request_list, port, n_logs, debug=False): #TODO: replace by debug=False when deploying
	""" Periodically save state of the app into csv
	"""

	# Don’t save the state in debug mode
	# to avoid unnecessary file creation in the development environment
	if debug:
		return n_logs

	port = pd.DataFrame.from_dict(port)

	df = pd.DataFrame({
		"host-timestamp": [datetime.now().timestamp()],
		"market-timestamp": [timestamp],
		"selected-company": [company_id],
		"cashflow": [cashflow]
	})
	# format portfolio info to be saved
	df = pd.concat([
		df,
		port.loc['Shares'].to_frame().rename(index={
			c : c + '-shares' for c in port.columns
		}, columns={'Shares':0}).T,
		port.loc['Total'].to_frame().rename(index={
			c : c + '-total' for c in port.columns
		}, columns={'Total':0}).T
	], axis=1)

	# Be sure that the request list has MAX_REQUESTS elements in the header (useful for the first time only)
	for i in range(MAX_REQUESTS):
	    df[f'request {i+1}'] = None

	# Prepare request list to be saved as columns
	df = df.combine_first(
		pd.DataFrame({
			f'request {i+1}': f"{rq[3]} {rq[0]} {rq[2]} {rq[1]}" \
			for i, rq in enumerate(request_list[:MAX_REQUESTS])
		}, index = [0])
	)

	# Reorder columns to be sure that the order is always the same
	df = df.reindex(sorted(df.columns), axis=1)

	# Save the header only once and append the rest
	file_path = os.path.join('Data', 'interface-logs.csv')
	if os.path.isfile(file_path):
		df.to_csv(file_path, mode='a', index=False, header=False)
	else:
		df.to_csv(file_path, index=False)

	return n_logs + 1


if __name__ == '__main__':
    app.run_server(debug=True) #TODO: change to False when deploying