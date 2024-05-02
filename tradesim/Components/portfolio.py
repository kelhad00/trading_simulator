import pandas as pd
from dash import html, Output, Input, State, page_registry as dash_registry
import dash

from tradesim.Locales import translations as tls
from tradesim.defaults import defaults as dlt

@dash.callback(
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


@dash.callback(
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

	# Replace the stock name by the company name
	df['Stock'] = df['Stock'].apply(lambda x: dlt.companies[x])

	stock_size = len(df)
	column_size = stock_size
	column_names = tls[dash_registry['lang']]['portfolio-columns']
	return html.Div([
		html.Table([
			html.Thead([
				html.Tr([
					html.Th(col) for col in column_names.values()
				])
			]),
			html.Tbody([
				html.Tr([
					html.Td( df.iloc[i][col] ) for col in column_names.keys()
				]) for i in range(j,column_size + j) if i < stock_size
			])
		]) for j in range(0, stock_size, column_size)
    ], className="portfolio-table")


@dash.callback(
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
		text['portfolio-cashflow'], round(cash, 2),' €\n',
		text['portfolio-investment'], round(cash + totals.sum(), 2),' €'
	]
