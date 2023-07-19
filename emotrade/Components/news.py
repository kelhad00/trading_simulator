import os
import pandas as pd
from dash import Output, Input, State
from dash.exceptions import PreventUpdate
import dash

from emotrade.defaults import defaults as dlt

@dash.callback(
	Output('news-dataframe','data'),
	Output('news-table','data'),
	Input('market-timestamp-value','data'),
	State('news-dataframe','data'),
)
def update_news_table(timestamp, news_df, range=1000, daily = True):
	""" Display one more news periodically
		Limit the number of news displayed to the range parameter
	"""
	# If the news dataframe is not loaded yet, load it
	if not news_df:
		try:
			file_path = os.path.join(dlt.data_path, 'news.csv')
			news_df = pd.read_csv(file_path, sep=';') \
						.drop_duplicates(subset=['title'], keep='first')\
						.rename({'title':'article'}, axis=1)
			news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True, format='mixed')
		except :
			print('You need to add the `news.csv` file into the ' + dlt.data_path + ' folder')
			raise PreventUpdate
	else:
		news_df = pd.DataFrame.from_dict(news_df)
		news_df['date'] = pd.to_datetime(news_df['date'])

	# Convert timestamp to datetime to the format used by the news dataframe
	timestamp = pd.to_datetime(timestamp).tz_localize(None)

	if daily:
		timestamp = timestamp + pd.Timedelta(days=1)

	# Get the news before the timestamp
	nl = news_df.loc[news_df['date'] <= timestamp].sort_values(by='date', ascending=False).astype(str)

	return news_df.to_dict(), nl[:range].to_dict('records')


@dash.callback(
	Output('news-container', 'style'),
	Output('description-title', 'children'),
	Output('description-text', 'children'),
	Output('description-container', 'style'),
	Input('news-table', 'active_cell'),
	State('news-table', 'data'),
)
def show_hide_element(cell_clicked, table):
	"""Hide News table & Show News description when News table cell clicked
	"""
	if not cell_clicked :
		return {'display': 'block'}, '', '', {'display': 'none'}

	# get the index of the cell clicked (dict) /!\ callback err ??
	index_clicked = cell_clicked['row']

	# Previous version :
	# get the title of the cell clicked (table = list & table[ind] = dict)
	# article_clicked = table[index_clicked]['article']

	# # find the description in the dtf with the title /!\ news_df = DICT
	# # getting the news data to find the content
	# file_path = os.path.join(dlt.data_path, 'news.csv')
	# news_df = pd.read_csv(file_path, sep=';', usecols=['title','content'])\

	# # getting the content of the corresponding article
	# text_description = news_df.loc[news_df['title'] == article_clicked]['content']

	article_clicked = table[index_clicked]['article']
	text_description = table[index_clicked]['content']

	# change the layout
	return {'display': 'none'}, article_clicked, text_description, {'display': 'block'}


# Button to go back to the Market News List
@dash.callback(
	Output('description-container', 'style', allow_duplicate=True),
	Output('news-container', 'style', allow_duplicate=True),
	Input('back-to-news-list', 'n_clicks'),
	prevent_initial_call=True,
)
def back_to_news(btn):
	return {'display': 'none'}, {'display': 'block'}

