import os
from datetime import datetime
import pandas as pd
from dash import Output, Input, State
import dash

from tradesim.defaults import defaults as dlt


@dash.callback(
	Output('nbr-logs', 'data'),
	# ** Data to save **
	# Changing the company doesn’t trigger other callbacks in every case
	Input('company-selector', 'value'),
	Input('news-table', 'data'), # indepedent variable
	# Clicking on a news doesn’t trigger other callbacks
	Input('description-container', 'style'),
	# Adding or removing a request doesn’t trigger other callbacks
	Input("request-list", "data"),
	Input('graph-tabs', 'value'),
	# Data triggered by those above
	# The timestamp isn’t an input because we want to save user moves
	# Others states that we need
	State('market-timestamp-value','data'),
	State('cashflow', 'data'),
	State('portfolio_shares', 'data'),
	State('portfolio_totals', 'data'),
	State('description-text', 'children'),
	State('nbr-logs', 'data') # number of times the callback has been called
)
def save_state(	company_id, news_df, news_description_style, request_list, selected_tab,\
				timestamp, cashflow, shares, totals, description_title, n_logs,\
				debug=False): #TODO: replace by debug=False when deploying
	""" Periodically save state of the trade into csv
	"""

	# Don’t save the state in debug mode
	# to avoid unnecessary file creation in the development environment
	if debug:
		return n_logs + 1

	news_df = pd.DataFrame.from_dict(news_df)
	shares = pd.DataFrame.from_dict(shares)
	totals = pd.DataFrame.from_dict(totals)

	df = pd.DataFrame({
		"host-timestamp": [datetime.now().timestamp()],
		"market-timestamp": [timestamp],
		"selected-company": [company_id],
		"selected-graph": [selected_tab],
		"cashflow": [cashflow],
		"last-news": [news_df.iloc[0]['article'] if not news_df.empty else ''],
		"nbr-news-displayed": [len(news_df)],
		"news-mode": ['news-table'],
		"selected-news": '', # if no news is selected then the description is empty
	})

	# If a news is selected, save the description
	if news_description_style['display'] == 'block':
		df['news-mode'] = 'news-description'
		df['selected-news'] = description_title

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
	for i in range(dlt.max_requests):
		df[f'request {i+1}'] = None

	# Prepare request list to be saved as columns
	df = df.combine_first(
		pd.DataFrame({
			f'request {i+1}': f"{rq[0]} {rq[1]} {rq[2]} {rq[3]}" \
			for i, rq in enumerate(request_list[:dlt.max_requests])
		}, index = [0])
	)

	# Reorder columns to be sure that the order is always the same
	df = df.reindex(sorted(df.columns), axis=1)

	# Save the header only once and append the rest
	file_path = os.path.join(dlt.data_path, 'interface-logs.csv')
	if os.path.isfile(file_path):
		df.to_csv(file_path, mode='a', index=False, header=False)
	else:
		df.to_csv(file_path, index=False)

	return n_logs + 1
