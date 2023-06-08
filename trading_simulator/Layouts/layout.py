from dash import html, dcc, dash_table
import pandas as pd

from trading_simulator import MAX_INV_MONEY, UPDATE_TIME, COMP, INDEX
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
	dcc.Store(id = 'portfolio_shares', data = {c: {'Shares': 0} for c in COMP.keys()}), # Store only the number of shares for each company
	dcc.Store(id = 'portfolio_totals', data = {c: {'Total': 0} for c in COMP.keys()}),   # Store only the total price for each company

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
			dcc.Dropdown({**COMP, **INDEX}, list(COMP.keys())[0],
				id='company-selector',
				clearable=False,
				style = {'padding-right' : 80, 'textAlign' : 'center'}
			),
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
			html.H2(children='Actualités du Marché'),
			dash_table.DataTable(
				id='news-table',
				columns=[{'name': 'Date', 'id': 'date'}, {'name': 'Article', 'id': 'article'}],
				style_cell={
					'padding': '2px 10px',
					'maxWidth': '30vw',
					'overflow': 'hidden',
        			'textOverflow': 'ellipsis',
					'textAlign': 'left',
				},
				# fixed_rows={'headers': True}, # for scrollbar (vertically) but doesn't work wih the update ??
				page_size=5,
			)
		], id ='news-container', style={'padding': 10, 'flex': 1}),

		# Add the component with the description
		html.Div(children=[
			html.H2(children = 'Description de l\'article'),
			html.P('Description/résumé de l\'article cliqué', id='description-text', style = {'textAlign' : 'center'}),
			html.Button('Retour', id = 'back-to-news-list', style={'border' : 'none', 'padding-top' : 5, 'padding-bottom' : 5, 'border-radius' : 10})
		], id='description-container', style={'padding': 10, 'flex': 1, 'display': 'none'}),


		# Requests
		html.Div(children=[
			html.H2('Faites une requêtes'),

			html.Label('Actions :', htmlFor='action-input'),
			dcc.RadioItems(['Vendre', 'Acheter'], "Acheter",id="action-input", inline=True),

			html.Label('Prix', htmlFor='price-input', style = {'margin-top' : 20}),
			dcc.Input(id='price-input', value=0,type='number',min=0, step=0.1),

			html.Label('Parts', htmlFor='nbr-share-input', style = {'margin-top' : 20}),
			dcc.Input(id='nbr-share-input',value=1, type='number',min=1, step=1),

			html.Button("Soumettre",id='submit-button', n_clicks=0, style={'border' : 'none', 'padding-top' : 5, 'padding-bottom' : 5, 'border-radius' : 10, 'margin-right' : 70, 'margin-left' : 70, 'margin-top' : 20})
		], style={'padding': 10, 'flex': 1, 'display': 'flex', 'flex-direction': 'column', 'margin-left': '5%', 'margin-right': '5%'}),

		html.Div(children=[
			html.H2('Listes Requêtes'),
			html.Table([
				html.Thead(
					html.Th(['Actions ','Parts ','Comp ','Prix '])
				)
			],id="title-table"),
			html.Div(id="request-container"),
			html.Br(),
			html.Button("Supprimer",id="clear-done-btn", style={'border' : 'none', 'padding-top' : 5, 'padding-bottom' : 5, 'padding-left' : 30, 'padding-right' : 30, 'border-radius' : 10, 'margin-left' : 20})
		], style={'padding': 10, 'flex': 1})

	], style={'display': 'flex', 'flex-direction': 'row', 'height': '48vh', 'margin-top' : 50})

], style = {'font-family': 'Arial'})