import os
import pandas as pd
from dash import Output, Input, State
import dash

from tradingsimulator.defaults import defaults as dlt

# Callbacks
@dash.callback(
    Output("market-dataframe", "data"),
	Output("price-dataframe", "data"),
	Output('market-timestamp-value', 'data', allow_duplicate=True),
    Input('company-selector', 'value'),
	State("price-dataframe", "data"),
	State('market-timestamp-value', 'data'),
	prevent_initial_call=True
)
def import_market_data(company_id, price_list, timestamp):
	""" Import market data from CSV file
	"""
	# Import market data
	try:
		file_path = os.path.join(dlt.data_path, 'market_data.csv')
		df = pd.read_csv(file_path, index_col=0, header=[0,1])
	except :
		print('ERROR: No market data found in ' + dlt.data_path + ' folder.')
		raise FileNotFoundError

	# Extract price list from market data
	if not price_list: # if the dataframe has not been loaded yet
		price_list = df.xs('Close', axis=1, level=1)
		price_list = price_list.to_dict()

	if timestamp == '':
		try:
			file_path = os.path.join(dlt.data_path, 'news.csv')
			news_df = pd.read_csv(file_path, sep=';', usecols=['date'])
			news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True, format='mixed')

			# set the timestamp to the older shared date between news and market data
			# if news_df is the newer one, set the timestamp to the first date share with news_df
			if news_df.min().date.strftime('%Y-%m-%d') > df.index.min()[:10]:
				timestamp = df.loc[df.index >= news_df.min().date.strftime('%Y-%m-%d')].index[0]
			else:
				timestamp = df.index.min()
		except :
			timestamp = df.index.min()

	return df[company_id].to_dict(), price_list, timestamp
