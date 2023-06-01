import os
import pandas as pd
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

from trading_simulator.app import app


@app.callback(
	Output('news-index','data'),
	Output('news-dataframe','data'),
	Output('news-table','data'),
	Input('market-timestamp-value','data'),
	State('news-dataframe','data'),
	State('news-index','data'),
)
def update_news_table(timestamp, news_df, idx, range=10):
	""" Display one more news every time the timestamp is updated
		Limit the number of news displayed to the range parameter
	"""
	# If the news dataframe is not loaded yet, load it
	if not news_df:
		file_path = os.path.join('Data', 'news.csv')
		news_df = pd.read_csv(file_path, sep=';', usecols=['article','date'])
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



@app.callback(
	Output(component_id = 'description-container', component_property = 'style'),
	Output(component_id = 'news-container', component_property = 'style'),
	Output(component_id = 'description-text', component_property = 'children'),
	Input(component_id = 'news-table', component_property = 'active_cell'),
	State(component_id = 'news-dataframe', component_property = 'data'),
	State(component_id = 'news-index', component_property = 'data')
	)
def show_hide_element(cell_clicked, news_df, idx):
	"""Hide News table & Show News description when News table cell clicked
	"""
	# get the dataFrame for the summary and title
	# Setup > news_scrapping

	# get the index of the cell clicked
	print(cell_clicked)

	text_description = 'Résumé de l\'article'

	# change the layout
	if not cell_clicked :
		return {'display': 'none'}, {'display': 'block', 'padding': 10, 'flex': 1}, text_description
		
	if cell_clicked :
		return {'display': 'block', 'padding': 10, 'flex': 1}, {'display': 'none'}, text_description


# Button to go back to the Market News List
@app.callback(
	Output(component_id = 'description-container', component_property = 'style', allow_duplicate=True),
	Output(component_id = 'news-container', component_property = 'style',allow_duplicate=True),
	Input(component_id = 'back-to-news-list', component_property = 'n_clicks'),
	prevent_initial_call=True,
)
def back_to_news(btn):
	return {'display': 'none'}, {'display': 'block', 'padding': 10, 'flex': 1}

