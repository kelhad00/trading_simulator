import os
import pandas as pd
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

from trading_simulator.app import app


@app.callback(
	Output('news-index','data'),
	Output('news-dataframe','data'),
	Output('news-table','data'),
	Input('periodic-updater','n_intervals'),
	State('news-dataframe','data'),
	State('news-index','data'),
)
def update_news_table(n, news_df, idx, range=10):
	""" Display one more news periodically
		Limit the number of news displayed to the range parameter
	"""
	# If the news dataframe is not loaded yet, load it
	if not news_df:
		file_path = os.path.join('Data', 'news.csv')
		news_df = pd.read_csv(file_path, sep=';', usecols=['article','date'])
		news_df = news_df[::-1].reset_index(drop=True)
	else:
		news_df = pd.DataFrame.from_dict(news_df)

	# While the index is not at the end of the dataframe, increment it
	# Otherwise, the index does not change and let the news table unchanged
	if idx >= len(news_df):
		raise PreventUpdate # Exit the callback without updating anything
	else:
		idx += 1

	nl = news_df.iloc[idx - range : idx].iloc[::-1]

	return idx, news_df.to_dict(), nl.to_dict('records')
