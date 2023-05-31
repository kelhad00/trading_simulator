import os
from datetime import datetime
import pandas as pd
from dash import Output, Input, State

from trading_simulator import MAX_REQUESTS
from trading_simulator.app import app

@app.callback(
	Output('nbr-logs', 'data'),
	# Data to save
	Input('market-timestamp-value','data'),
	Input('company-selector', 'value'),
	Input('cashflow', 'data'),
	Input('request-list', 'data'),
	Input('news-index', 'data'),
	Input('portfolio_totals', 'data'),
	State('portfolio_shares', 'data'),
	State('news-dataframe', 'data'),
	# number of logs
	State('nbr-logs', 'data')
)
def save_state(timestamp, company_id, cashflow, request_list, news_id, totals, shares, news_df, n_logs, debug=False): #TODO: replace by debug=False when deploying
	""" Periodically save state of the app into csv
	"""

	# Don’t save the state in debug mode
	# to avoid unnecessary file creation in the development environment
	if debug:
		return n_logs

	news_df = pd.DataFrame.from_dict(news_df)
	shares = pd.DataFrame.from_dict(shares)
	totals = pd.DataFrame.from_dict(totals)

	df = pd.DataFrame({
		"host-timestamp": [datetime.now().timestamp()],
		"market-timestamp": [timestamp],
		"selected-company": [company_id],
		"cashflow": [cashflow],
		"last-news": [news_df.iloc[news_id - 1]['article']],
		"last-news-id": [news_id],
	})
	# format portfolio info to be saved
	df = pd.concat([
		df,
		shares.rename(
			# Add '-shares' to each column name to avoid duplicates
			columns={ c : c + '-shares' for c in shares.columns},
			index={'Shares':0} # Remove index name to have only one row
		),
		totals.rename(
			# Add '-total' to each column name to avoid duplicates
			columns={ c : c + '-total' for c in totals.columns},
			index={'Total':0} # Remove index name to have only one row
		),
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
