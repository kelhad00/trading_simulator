from dash import html, dcc, dash_table
import pandas as pd

from emotrade import MAX_INV_MONEY, UPDATE_TIME, COMP, INDEX
from emotrade.Components.candlestick_charts import PLOTLY_CONFIG
from emotrade.Locales import translations as tls


# Global variables
# Provide these components in global scope to keep their state between page changes
global_variables = [
    dcc.Store(id = 'nbr-logs', data = 0), # Number of times the app state has been saved
    # Store timestamp value in the browser
    dcc.Store(id = 'market-timestamp-value', data = '', storage_type='local'),
    dcc.Store(id = 'market-dataframe'),
    dcc.Store(id = 'price-dataframe'),
    dcc.Store(id = 'news-dataframe'),
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
]


# Layout of the app
def main_layout(lang="fr"):
	return html.Div([
		# Periodic updater
		dcc.Interval(
			id='periodic-updater',
			interval=UPDATE_TIME, # in milliseconds
		),

		# TODO: Remove this temporary button
		# Dropdown to change the language
		html.Div([
			dcc.Link( l, href=f'/{l}/dashboard', style = {
				'display': 'block',
				'padding': '0.7em 0.5em',
				'color': '#2f3238',
				'margin': '0.1em 0',
				'text-decoration': 'none',
				'background': '#fff',
				'border-radius': '4px',
				'border': '1px solid #ccc',
			}) for l in tls.keys() if l != lang
		], style = {'width' : '60px', 'position' : 'absolute', 'top': '10px', 'right': '10px'}),


		# Upper part
		html.Div([
			# Portfolio
			html.Div(children=[
				html.H2(children=tls[lang]['portfolio']),
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
					dcc.Tab(label=tls[lang]['tab-market'], value='tab-market', children=[
						dcc.Graph(
							id='company-graph',
							figure={'layout': {'height': 300}},
							# config = PLOTLY_CONFIG,
							config = {**PLOTLY_CONFIG, "locale": lang},
							style={'padding': 30}
						)
					]),
					dcc.Tab(label=tls[lang]['tab-revenue'], value='tab-revenue', id='tab-revenue', children=[
						dcc.Graph(
							id='revenue-graph',
							figure={'layout': {'height': 100}},
							config = {**PLOTLY_CONFIG, "locale": lang},
							style={'padding': 30, 'height': 300}
						),
					]),
				], style={'height': '44px', 'width': '92%', 'margin': '5px'}),
			], style={'padding-top': 30, 'flex': 3, 'margin-left' : 50})
		], style={'display': 'flex', 'flex-direction': 'row', 'height': '48vh'}),

		# Lower part
		html.Div([
			# News
			html.Div(children=[
				html.H2(children=tls[lang]['news']),
				dash_table.DataTable(
					id='news-table',
					columns=[
						{'name': tls[lang]['news-table']['date'], 'id': 'date'},
						{'name': tls[lang]['news-table']['article'], 'id': 'article'}
					],
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
				html.H2(children = tls[lang]['title-news-description']),
				html.P(id='description-text', style = {'textAlign' : 'center'}),
				html.Button(tls[lang]['button-news-description'], id = 'back-to-news-list',
					style={'border' : 'none', 'padding-top' : 5, 'padding-bottom' : 5, 'border-radius' : 10}
				)
			], id='description-container', style={'padding': 10, 'flex': 1, 'display': 'none'}),


			# Requests
			html.Div(children=[
				html.H2(tls[lang]['request-title']),

				html.Label(tls[lang]['request-action']['label'], htmlFor='action-input'),
				dcc.RadioItems(
					options=tls[lang]['request-action']['choices'],
					value='buy',
					id="action-input",
					inline=True
				),

				html.Label(tls[lang]['request-price'], htmlFor='price-input', style = {'margin-top' : 20}),
				dcc.Input(id='price-input', value=0,type='number',min=0, step=0.1),

				html.Label(tls[lang]['request-shares'], htmlFor='nbr-share-input', style = {'margin-top' : 20}),
				dcc.Input(id='nbr-share-input',value=1, type='number',min=1, step=1),

				html.Button(tls[lang]['submit-request'],id='submit-button', n_clicks=0, style={'border' : 'none', 'padding' : '5px 30px', 'border-radius' : 10, 'margin' : '20px 70px'}),

				html.P(id='request-err', style = {'color' : 'red'})
			], style={'padding': 10, 'flex': 1, 'display': 'flex', 'flex-direction': 'column', 'margin-left': '5%', 'margin-right': '5%'}),

			html.Div(children=[
				html.H2(tls[lang]['requests-list-title']),
				dash_table.DataTable(
					id='request-table',
					columns=[
						{'name': tls[lang]['requests-table']['actions'], 'id':'actions'},
						{'name': tls[lang]['requests-table']['shares'], 'id':'shares'},
						{'name': tls[lang]['requests-table']['company'], 'id': 'company'},
						{'name': tls[lang]['requests-table']['price'], 'id': 'price'}
					],
					row_selectable='multi',
					selected_rows=[],
					cell_selectable=False,
					style_cell={'padding': '2px 10px'},
					style_table={'width': '20vw'}
				),
				html.Button(tls[lang]['clear-all-requests-button'], id="clear-done-btn",
					style={'border' : 'none', 'padding' : '5px 30px', 'border-radius' : 10, 'width': '8vw', 'margin' : '20px 70px'}
				),
			], style={'padding': 10, 'flex': 2})

		], style={'display': 'flex', 'flex-direction': 'row', 'height': '48vh', 'margin-top' : 50})

	], style = {'font-family': 'Arial'})