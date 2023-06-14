import pandas as pd
from dash import html, Output, Input, State, page_registry as dash_registry

from emotrade.app import app
from emotrade.Locales import translations as tls

@app.callback(
	Output('portfolio_totals', 'data'),
	Input('periodic-updater', 'n_intervals'),
	Input('portfolio_shares', 'data'),
	State('portfolio_totals', 'data'),
	State('price-dataframe', 'data'),
	State('market-timestamp-value', 'data')
)
def update_porfolio_totals(n, shares, totals, price_df, timestamp):
	""" Update the portfolio total price with the latest market data price
	"""
	price_df = pd.DataFrame.from_dict(price_df)
	shares = pd.DataFrame.from_dict(shares).loc['Shares']
	df = pd.DataFrame.from_dict(totals)

	# Update the total price of each stock
	df.loc['Total'] = shares * price_df.loc[timestamp, df.columns]
	return df.to_dict()


@app.callback(
	Output('portfolio-table-container', 'children'),
	Input('portfolio_totals', 'data'),
	State('portfolio_shares', 'data')
)
def generate_portfolio_table(stocks_info, shares):
	""" Update the portfolio table with the latest user's portfolio information
	"""
	df = pd.concat([
		pd.DataFrame.from_dict(shares),
		pd.DataFrame.from_dict(stocks_info)
	]).transpose().round(2)
	df['Stock'] = df.index

	column_size = 10
	stock_size = len(df)
	column_names = tls[dash_registry['lang']]['portfolio-columns']
	return html.Div([
		html.Table([
			html.Thead([
				html.Tr([
					html.Th(
						col,
						style={'padding-right': 50,'border-color': '#d3d3d3', 'border-style': 'solid','border-width': '1px'}
					) for col in column_names.values()
				], style = {'background-color': '#fafafa'})
			]),
			html.Tbody([
				html.Tr([
					html.Td(
						df.iloc[i][col],
						style={'border-color': '#d3d3d3', 'border-style': 'solid', 'border-width': '1px'}
					) for col in column_names.keys()
				]) for i in range(j,column_size + j)
			])
		]) for j in range(0, stock_size, column_size)
    ], style={'display': 'flex', 'flex-direction': 'row'})


@app.callback(
	Output('portfolio-total-price', 'children'),
	Input('portfolio_totals', 'data'),
	State('cashflow', 'data')
)
def calcul_prix_tot_inv(stock_info, cash):
	""" Update the portfolio total price
	"""
	totals = pd.DataFrame.from_dict(stock_info, orient='index')['Total']
	text = tls[dash_registry['lang']]
	return [
		text['portfolio-cashflow'], round(cash, 2),' eur.\n',
		text['portfolio-investment'], round(cash + totals.sum(), 2),' eur.'
	]
