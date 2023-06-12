from dash import html, dcc, dash_table
import pandas as pd

from emotrade import MAX_INV_MONEY, UPDATE_TIME, COMP, INDEX
from emotrade.Components.candlestick_charts import PLOTLY_CONFIG

# Layout of the app
main_layout = html.Div([

	# Global variables
	dcc.Store(id = 'nbr-logs', data = 0), # Number of times the app state has been saved
	# Store timestamp value in the browser
	dcc.Store(id = 'market-timestamp-value', data = '', storage_type='local'),
	dcc.Store(id = 'market-dataframe'),
	dcc.Store(id = 'price-dataframe'),
	dcc.Store(id = 'news-dataframe'),
	# Display 10 news at the first load (0-9)
	dcc.Store(id = 'news-index', data = 9, storage_type='local'),
	dcc.Store(id = 'cashflow', data = MAX_INV_MONEY, storage_type='local'),
	dcc.Store(id = 'request-list', data = [], storage_type='local'),
	dcc.Store(  # Store only the number of shares for each company
		id = 'portfolio_shares',
		data = {c: {'Shares': 0} for c in COMP.keys()},
		storage_type='local'
	),
	dcc.Store(    # Store only the total price for each company
		id = 'portfolio_totals',
		data = {c: {'Total': 0} for c in COMP.keys()},
		storage_type='local'
	),
	dcc.Store(id = 'news_historic', data = []),

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
			dcc.Markdown(id='portfolio-total-price')
		], style={'padding': 10, 'flex': 2}),

		# Company graph
		html.Div(children=[
			dcc.Dropdown({**COMP, **INDEX}, list(COMP.keys())[0],
				id='company-selector',
				clearable=False,
				persistence = True,
				persistence_type = 'local',
				style = {'padding-right' : 80, 'textAlign' : 'center'}
			),
			dcc.Tabs(id="graph-tabs", value='tab-market', children=[
				dcc.Tab(label='Analyse Technique', value='tab-market', children=[
					dcc.Graph(
						id='company-graph',
						figure={'layout': {'height': 300}},
						config = PLOTLY_CONFIG,
						style={'padding': 30}
					)
				]),
        		dcc.Tab(label='Revenue', value='tab-revenue', id='tab-revenue', children=[
					dcc.Graph(
						id='revenue-graph',
						figure={'layout': {'height': 100}},
						config = PLOTLY_CONFIG,
						style={'padding': 30, 'height': 300}
					)
				]),
    		], style={'height': '44px', 'width': '92%', 'margin': '5px'}),
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
				style_table={'height': '35vh'},
				style_cell={
					'padding': '2px 10px',
					'maxWidth': '30vw',
					'overflow': 'hidden',
        			'textOverflow': 'ellipsis',
					'textAlign': 'left',
				},
				fixed_rows={'headers': True, 'data': 0}, # Allow to scroll the table
				page_size=1000000000, # Display all the news on the same page
			)
		], id ='news-container', style={'padding': 10, 'flex': 1}),

		# Add the component with the description
		html.Div(children=[
			html.H2(children = 'Description de l\'article'),
			html.P('Description/résumé de l\'article cliqué', id='description-text', style = {'textAlign' : 'center'}),
			html.Button('Retour', id = 'back-to-news-list',
				style={'border' : 'none', 'padding-top' : 5, 'padding-bottom' : 5, 'border-radius' : 10}
			)
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

			html.Button("Soumettre",id='submit-button', n_clicks=0, style={'border' : 'none', 'padding' : '5px 30px', 'border-radius' : 10, 'margin' : '20px 70px'}),

			html.P(id='request-err', style = {'color' : 'red'})
		], style={'padding': 10, 'flex': 1, 'display': 'flex', 'flex-direction': 'column', 'margin-left': '5%', 'margin-right': '5%'}),

		html.Div(children=[
			html.H2('Listes Requêtes'),
			dash_table.DataTable(
				id='request-table',
				columns=[
					{'name': 'Actions', 'id':'actions'},
					{'name': 'Parts', 'id':'shares'},
					{'name': 'Compagnie', 'id': 'company'},
					{'name': 'Prix ', 'id': 'price'}
				],
				row_selectable='multi',
				selected_rows=[],
				cell_selectable=False,
				style_cell={'padding': '2px 10px'},
				style_table={'width': '20vw'}
			),
			html.Button("Supprimer tout", id="clear-done-btn",
				style={'border' : 'none', 'padding' : '5px 30px', 'border-radius' : 10, 'width': '8vw', 'margin' : '20px 70px'}
			),
		], style={'padding': 10, 'flex': 2})

	], style={'display': 'flex', 'flex-direction': 'row', 'height': '48vh', 'margin-top' : 50})

], style = {'font-family': 'Arial'})