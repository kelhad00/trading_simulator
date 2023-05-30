from dash import html, dcc, dash_table

from trading_simulator import MAX_INV_MONEY, UPDATE_TIME, COMP
from trading_simulator.Components.candlestick_charts import PLOTLY_CONFIG

# Layout of the app
main_layout = html.Div([

	# Global variables
	dcc.Store(id = 'nbr-logs', data = 0),                # Number of times the app state has been saved
	dcc.Store(id = 'market-timestamp-value', data = ''), # Store timestamp value in the browser
	dcc.Store(id = 'market-dataframe'),                  # Store market data in the browser
	dcc.Store(id = 'price-dataframe'),                   # Store market data in the browser
	dcc.Store(id = 'news-dataframe'),
	dcc.Store(id = 'news-index', data = 9),              # Display 10 news at the first load (0-9)
	dcc.Store(id = 'cashflow', data = MAX_INV_MONEY),
	dcc.Store(id = 'request-list', data = []),
	dcc.Store(id = 'liste-skiprows', data=[6,7,8,9,10]), #still necessary ? 
	dcc.Store(id = 'portfolio_info', data = {c: {'Shares': 0, 'Total': 0} for c in COMP.keys()}),

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
			html.H2(children='Portfolio', style = {'font-family': 'Arial'}),
			html.Div(id='portfolio-table-container'),
			dcc.Markdown(id='portfolio-total-price')
		], style={'padding': 10, 'flex': 2, 'font-family': 'Arial'}),

		# Company graph
		html.Div(children=[
			dcc.Dropdown(COMP, list(COMP.keys())[0], id='company-selector', clearable=False, style = {'font-family': 'Arial', 'padding-right' : 80, 'textAlign' : 'center'}),
			dcc.Graph(
				id='company-graph',
				figure={'layout': {'height': 300}},
				config = PLOTLY_CONFIG,
				style={'padding': 30}
			)
		], style={'padding-top': 30, 'flex': 3, 'margin-left' : 50})
	], style={'display': 'flex', 'flex-direction': 'row', 'height': '48vh'}),

	# Lower part
	html.Div([
		# News
		html.Div(children=[
			html.H2(children='Market News', style = {'font-family': 'Arial'}),
			dash_table.DataTable(
				id='news-table',
				columns=[{'name': 'Date', 'id': 'date'}, {'name': 'Article', 'id': 'article'}],
				style_cell={'textAlign': 'left', 'padding': '2px 10px', 'font-family': 'Arial'},
			)
		], style={'padding': 10, 'flex': 1}),

		# Requests
		html.Div(children=[
			html.H2('Make A Request', style = {'font-family': 'Arial'}),

			html.Label('Actions :', htmlFor='action-input', style = {'font-family': 'Arial'}),
			dcc.RadioItems(['Buy', 'Sell'], "Buy",id="action-input", inline=True, style = {'font-family': 'Arial'}),

			html.Br(),
			html.Label('Price', htmlFor='price-input', style = {'font-family': 'Arial'}),
			dcc.Input(id='price-input', value=0,type='number',min=0, step=0.1, style = {'font-family': 'Arial'}),

			html.Br(),
			html.Label('Shares', htmlFor='nbr-share-input', style = {'font-family': 'Arial'}),
			dcc.Input(id='nbr-share-input',value=1, type='number',min=1, step=1, style = {'font-family': 'Arial'}),

			html.Br(),
			html.Button("Submit",id='submit-button', n_clicks=0,style={'border' : 'none', 'padding-top' : 5, 'padding-bottom' : 5, 'border-radius' : 10, 'margin-right' : 90, 'margin-left' : 90})
		], style={'padding': 10, 'flex': 1, 'display': 'flex', 'flex-direction': 'column', 'margin-left': '5%', 'margin-right': '5%'}),

		html.Div(children=[
			html.H2('Request List', style = {'font-family': 'Arial'}),
			html.Table([
				html.Thead(
					html.Tr(['Price ','Shares ','Comp ','Actions '])
				)
			],id="title-table", style = {'font-family': 'Arial'}),
			html.Div(id="request-container"),
			html.Br(),
			html.Button("Clear",id="clear-done-btn", style={'border' : 'none', 'padding-top' : 5, 'padding-bottom' : 5, 'padding-left' : 30, 'padding-right' : 30, 'border-radius' : 10, 'margin-left' : 20})
		], style={'padding': 10, 'flex': 1})

	], style={'display': 'flex', 'flex-direction': 'row', 'height': '48vh', 'margin-top' : 50})

])