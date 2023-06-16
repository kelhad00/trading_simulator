import os
import pandas as pd
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

from emotrade.app import app


@app.callback(
	Output('news-dataframe','data'),
	Output('news-table','data'),
	Input('market-timestamp-value','data'),
	State('news-dataframe','data'),
)
def update_news_table(timestamp, news_df):
	""" Display one more news periodically
		Limit the number of news displayed to the range parameter
	"""
	# If the news dataframe is not loaded yet, load it
	if not news_df:
		file_path = os.path.join('Data', 'news.csv')
		news_df = pd.read_csv(file_path, sep=';')
		news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True)
	else:
		news_df = pd.DataFrame.from_dict(news_df)
		news_df['date'] = pd.to_datetime(news_df['date'])

	# Convert timestamp to datetime to the format used by the news dataframe
	timestamp = pd.to_datetime(timestamp).tz_localize(None)

	# Get the news before the timestamp
	nl = news_df.loc[news_df['date'] <= timestamp].sort_values(by='date', ascending=False).astype(str)

	return news_df.to_dict(), nl.to_dict('records')


@app.callback(
	Output(component_id = 'news-container', component_property = 'style'),
	Output(component_id = 'description-text', component_property = 'children'),
	Output(component_id = 'description-container', component_property = 'style'),
	Output(component_id = 'news_historic', component_property = 'data'),
	Input(component_id = 'news-table', component_property = 'active_cell'),
	State(component_id = 'news-table', component_property = 'data'),
	State(component_id = 'news_historic', component_property = 'data'),
	)
def show_hide_element(cell_clicked, table, news_historic):
	"""Hide News table & Show News description when News table cell clicked
	"""
	if not cell_clicked :
		return {'display': 'block', 'padding': 10, 'flex': 1}, '', {'display': 'none'}, news_historic

	# get the index of the cell clicked (dict) /!\ callback err ??
	index_clicked = cell_clicked['row']

	# get the title of the cell clicked (table = list & table[ind] = dict)
	article_clicked = table[index_clicked]['article']

	# find the description in the dtf with the title /!\ news_df = DICT
	# getting the news data to find the content
	file_path = os.path.join('Data', 'news.csv')
	news_df = pd.read_csv(file_path, sep=';')

	# getting the content of the corresponding article
	www = news_df.loc[news_df['article'] == article_clicked]
	text_description = www['ticker'] # change to the summary

	# keeping an historic of the clicked articles
	ww = www.values.tolist()
	news_historic.append(ww[0])

	# change the layout
	return {'display': 'none'}, text_description, {'display': 'block', 'padding': 10, 'flex': 1}, news_historic


# Button to go back to the Market News List
@app.callback(
	Output(component_id = 'description-container', component_property = 'style', allow_duplicate=True),
	Output(component_id = 'news-container', component_property = 'style', allow_duplicate=True),
	Input(component_id = 'back-to-news-list', component_property = 'n_clicks'),
	prevent_initial_call=True,
)
def back_to_news(btn):
	return {'display': 'none'}, {'display': 'block', 'padding': 10, 'flex': 1}

