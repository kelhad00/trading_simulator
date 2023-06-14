import pandas as pd
from dash import html, dcc, Output, Input, State, Patch, no_update, page_registry as dash_registry

import emotrade as etd
from emotrade.app import app
from emotrade.Locales import translations as tls


@app.callback(
	Output("price-input", "disabled"),
	Output("nbr-share-input", "disabled"),
	Output("submit-button", "disabled"),
	Input("company-selector", "value"),
)
def change_state_request_form(company):
	""" Disable the request form when an index is selected
		And enable it want a company is selected
	"""
	if company in etd.INDEX.keys():
		return True, True, True # Disable the form
	else:
		return False, False, False # Enable the form


@app.callback(
	Output("request-list", "data", allow_duplicate=True),
	Output('request-err', 'hidden'),
	Output('request-err', 'children'),
	# Form inputs
    Input("submit-button", "n_clicks"),
	State("company-selector", "value"),
	State("action-input","value"),
    State("price-input", "value"),
	State("nbr-share-input", "value"),
	State('cashflow','data'),
	# Needed to check if the user can execute the request
	State('market-timestamp-value','data'),
	State('price-dataframe','data'),
	State('portfolio_shares','data'),
	# Needed to update the request list
	State("request-list", "data"),
    prevent_initial_call=True,
)
def add_request(btn, company, action, price, share, cash, timestamp, price_list, port_shares, req):

    # If the user has too many requests
	if len(req) == etd.MAX_REQUESTS:
		return no_update, False, tls[dash_registry['lang']]["err-too-many-requests"]

	# If the form isn't filled correctly
	if price == 0 and btn != 0:
		return no_update, False, tls[dash_registry['lang']]["err-wrong-form"]

	stock_price = pd.DataFrame.from_dict(price_list)[company].loc[timestamp]
	# If the request is to buy and the user doesn't have enough money
	if action == 'buy' and cash < share * stock_price:
		return no_update, False, tls[dash_registry['lang']]["err-enough-money"]

	# If the request is to sell and the user doesn't have enough shares
	if action == 'sell' and share > port_shares[company]['Shares']:
		return no_update, False, tls[dash_registry['lang']]["err-enough-shares"].format(company)

	# Add the request to the request list
	req.append([action,share,company,price])

	return req, True, ''


@app.callback(
	Output("request-table", "data"),
	Input("request-list", "data"),
)
def display_requests(req):
	return  pd.DataFrame(req,
		columns=['actions', 'shares', 'company', 'price']
	).replace(tls[dash_registry['lang']]['request-action']['choices']).to_dict('records')


@app.callback(
    Output("request-list", "data"),
	Output("portfolio_shares", "data"),
	Output("cashflow", "data"),
	Input('market-timestamp-value','data'),
    State("request-list", "data"),
	State('price-dataframe','data'),
	State('portfolio_shares','data'),
	State('cashflow','data'),
)
def exec_request(timestamp, request_list, list_price, portfolio_info, cashflow):
	list_price = pd.DataFrame.from_dict(list_price)
	portfolio_info = pd.DataFrame.from_dict(portfolio_info)

	i = 0
	while i < len(request_list):
		req = request_list[i]
		stock_price = list_price[req[2]].loc[timestamp]

		# If the request is completed
		if req[0] == 'buy' and req[3] >= stock_price:
			# If the user has enough money
			if req[1] * stock_price < cashflow:

				# Update only the shares and the cashflow
				# Because the total price will be updated in the portfolio callback
				portfolio_info.loc['Shares', req[2]] += req[1]
				cashflow -= req[1] * stock_price

			# the request is removed, with or without the user having enough money
			request_list.remove(req)

		# Same as above for the sell request
		elif req[0] == 'sell' and req[3] <= stock_price:
			# If the user has enough shares
			if portfolio_info.loc['Shares', req[2]] >= req[1]:

				# Update only the shares and the cashflow
				# Because the total price will be updated in the portfolio callback
				portfolio_info.loc['Shares', req[2]] -= req[1]
				cashflow += req[1] * stock_price

			# the request is removed, with or without the user having enough shares
			request_list.remove(req)

		# If the request is not completed yet, pass to the next one.
		# If the request is completed, the request is removed from the list and
		# the next request is now at the current index.
		else:
			i += 1

	return request_list, portfolio_info.to_dict(), cashflow

@app.callback(
	Output('clear-done-btn', 'children'),
	Input('request-table', 'selected_rows'),
)
def switch_between_delete_and_delete_all(selected_rows):
	if len(selected_rows) == 0:
		return  tls[dash_registry['lang']]["clear-all-requests-button"]
	else:
		return  tls[dash_registry['lang']]["clear-requests-button"]


# Callback to delete items marked as done
@app.callback(
	Output("request-list", "data", allow_duplicate=True),
	Output("request-table", "selected_rows"),
	Input('clear-done-btn', 'n_clicks'),
	State("request-table", "selected_rows"),
	prevent_initial_call=True
)
def remove_request(n, values_to_remove):
	request_list = Patch()

	if values_to_remove == []:
		request_list = []

	for v in values_to_remove:
		del request_list[v]

	return request_list, []
