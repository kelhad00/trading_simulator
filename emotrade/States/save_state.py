import os
from datetime import datetime
import pandas as pd
from dash import Output, Input, State

from emotrade import MAX_REQUESTS
from emotrade.app import app

@app.callback(
	Output('nbr-logs', 'data'),
	# ** Data to save **
	# Changing the company doesn’t trigger other callbacks in every case
	Input('company-selector', 'value'),
	Input('news-index', 'data'), # indepedent variable
	# the cashflow is triggered by the timestamp so
	# we use it to call the callback as late as possible
	Input('cashflow', 'data'),
	# Adding or removing a request doesn’t trigger other callbacks
	Input('request-list', 'data'),
	Input('graph-tabs', 'value'),
	# Data triggered by those above
	# The timestamp isn’t an input because
	# we want to save the state after all changes are done
	# ( A callback is not triggered multiple times
	#   if multiple inputs change at the same time )
	State('market-timestamp-value','data'),
	State('portfolio_shares', 'data'),
	State('portfolio_totals', 'data'),
	State('news-dataframe', 'data'),
	# ** End of data to save **
	State('nbr-logs', 'data') # number of times the callback has been called
)
def save_state(company_id, news_id, cashflow, request_list, selected_tab, timestamp, shares, totals, news_df, n_logs, debug=False): #TODO: replace by debug=False when deploying
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
		"selected-tab": [selected_tab],
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
			f'request {i+1}': f"{rq[0]} {rq[1]} {rq[2]} {rq[3]}" \
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
