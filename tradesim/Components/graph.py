import os
import pandas as pd
from dash import Output, Input, State, ctx, no_update, page_registry as dash_registry
from dash.exceptions import PreventUpdate
import dash
import plotly.graph_objects as go

from tradesim.Components.candlestick_charts import create_graph
from tradesim.defaults import defaults as dlt
from tradesim.Locales import translations as tls


@dash.callback(
	Output('company-graph', 'figure'),          # new graph
	Output('market-timestamp-value', 'data'),   # new timestamp
	Input('periodic-updater', 'n_intervals'), 	# periodicly updated
	Input('market-dataframe', 'data'),          # new company is selected
	State('market-timestamp-value', 'data') 	# Last timestamp
)
def update_graph(n, df, timestamp, range=100):
	""" Update the graph with the latest market data
		Periodicly updated or when the user selects a new company
	"""
	# Determining which callback input changed
	if ctx.triggered_id == 'periodic-updater':
		next_graph = True
	else:
		# If the user selected a new company
		# Don’t change the timestamp.
		next_graph = False

	dftmp = pd.DataFrame.from_dict(df)
	fig, timestamp = create_graph(
		dftmp,
        timestamp,
		next_graph,
        range
    )
	# Define chart layout
	fig.update_layout(
		# xaxis_title = tls[dash_registry['lang']]["market-graph"]['x'],
        # yaxis_title = tls[dash_registry['lang']]["market-graph"]['y'],
        yaxis_tickprefix = '€',
        margin = dict(l=0, r=0, t=0, b=0),
        height = 300,
		legend = dict(x=0, y=1.0)
    )
	# Change language on the legend
	fig.for_each_trace(lambda t:
		t.update(name = tls[dash_registry['lang']]["market-graph"]['legend'][t.name])
	)

	return fig, timestamp


@dash.callback(
	Output('revenue-graph', 'figure'),
	Output('graph-tabs', 'value'),
	Output('tab-revenue', 'style'),
	Input('company-selector', 'value'),
	Input('market-timestamp-value','data'),
)
def update_revenue( company, timestamp):
	""" Display the revenue graph
	"""
	# If the user select an index, force the tab to be the market graph
	if company in dlt.indexes.keys():
		return no_update, 'tab-market', {'display': 'none'}

	timestamp = pd.to_datetime(timestamp)

	# When it's the timestamp that calls the callback,
	# it's possible that a new year is available, so update the information.
	# Otherwise, nothing is done.
	# We therefore only check if an additional year is available,
	# if the current timestamp is the first week of the year.
	# if ctx.triggered_id == 'market-timestamp-value' and timestamp.week > 1:
	# 	raise PreventUpdate
	# Using this method prevents income from being displayed
	# for as long as the user has not changed company,
	# unless it's the first week of the year.
	# TODO: So we need to find another way of optimizing

	# Import income data of the selected company
	file_path = os.path.join(dlt.data_path, 'revenue.csv')
	df = pd.read_csv(file_path, index_col=0, header=[0,1])

	# Format these data to be easily used
	df = df[company].T.reset_index()
	df['asOfDate'] = pd.to_datetime(df['asOfDate']).dt.year
	df['NetIncome'] = pd.to_numeric(df['NetIncome'], errors='coerce')
	df['TotalRevenue'] = pd.to_numeric(df['TotalRevenue'], errors='coerce')

	# Filter the data to only keep the data from the previous years
	year = timestamp.year
	df = df.loc[df['asOfDate'] < year]

	# Create the graph
	fig = go.Figure(data=[
		go.Bar(
			name = tls[dash_registry['lang']]["revenue-graph"]['totalRevenue'],
			x = df['asOfDate'], y = df['TotalRevenue']
		),
		go.Bar(
			name = tls[dash_registry['lang']]["revenue-graph"]['netIncome'],
			x = df['asOfDate'], y = df['NetIncome']
		)
	])
	fig.update_layout(
		yaxis_tickprefix = '€',
        margin = dict(l=0, r=0, t=0, b=0),
        height = 300,
		legend=dict(x=0, y=1.0)
	)

	if ctx.triggered_id == 'company-selector':
		# Go back to the market graph when the user selects a new company
		return fig, 'tab-market', {'display': 'block'}
	else:
		# If new information has been added, add it to the revenue graph,
		# but don't change anything else.
		return fig, no_update, no_update