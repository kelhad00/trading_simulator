import pandas as pd
from dash import html, dcc, Output, Input, State, Patch, ALL

import trading_simulator as ts
from trading_simulator.app import app

@app.callback(
    Output(component_id="request-container", component_property="children", allow_duplicate=True),
	Output("request-list", "data", allow_duplicate=True),
	Output('many-request', 'displayed'),    # Error message if the user has too many requests
	Output('form-not-filled', 'displayed'), # Error message if the form isn't filled correctly
    Input("submit-button", "n_clicks"),
    State("price-input", "value"),
	State("nbr-share-input", "value"),
	State("company-selector", "value"),
	State("action-input","value"),
	State("request-list", "data"),
    prevent_initial_call=True,
)
def ajouter_requetes(btn,price,share,company,action,req):
	patched_list = Patch()

    # If the user has too many requests
	if len(req) == ts.MAX_REQUESTS:
		return patched_list, req, True, False

	# If the form isn't filled correctly
	if price == 0 and btn != 0:
		return patched_list, req, False, True

	# Add the request to the list
	value = [price,share,company,action]
	req.append(value)

	def generate_line(value):
		return html.Div(
			[
				html.Div(
					str(value),
					id={"index": len(req), "type": "output-str"},
					style={"display": "inline", "margin": "10px"},
				),
				dcc.Checklist(
					options=[{"label": "", "value": "done"}],
					id={"index": len(req), "type": "done"},
					style={"display": "inline"},
					labelStyle={"display": "inline"},
				),
			]
		)

	# Show the request list on the interface
	patched_list.append(generate_line(value))

	return patched_list, req, False, False


@app.callback(
    Output("request-container", "children", allow_duplicate=True),
    Output("request-list", "data"),
	Output("portfolio_info", "data"),
	Output("cashflow", "data"),
	Input('market-timestamp-value','data'),
    State("request-list", "data"),
	State('price-dataframe','data'),
	State('portfolio_info','data'),
	State('cashflow','data'),
	prevent_initial_call=True
)
def exec_request(timestamp, request_list, list_price, portfolio_info, cashflow):
	patched_list = Patch() # Get request-container children
	list_price = pd.DataFrame.from_dict(list_price)
	portfolio_info = pd.DataFrame.from_dict(portfolio_info)

	i = 0
	while i < len(request_list):
		req = request_list[i]
		stock_price = list_price[req[2]].loc[timestamp]

		# If the request is completed
		if req[3] == 'Acheter' and req[0] >= stock_price:
			# If the user has enough money
			if req[1] * stock_price < cashflow:
				portfolio_info.loc['Parts', req[2]] += req[1]
				portfolio_info.loc['Total', req[2]] += req[1] * stock_price
				cashflow -= req[1] * stock_price
			# the request is removed, with or without the user having enough money
			del patched_list[i]
			request_list.remove(req)

		# Same as above for the sell request
		elif req[3] == 'Vendre' and req[0] <= stock_price:
			# If the user has enough shares
			if portfolio_info.loc['Parts', req[2]] >= req[1]:

				portfolio_info.loc['Parts', req[2]] -= req[1]
				cashflow += req[1] * stock_price

				# TODO: Find another way to fix total not a 0 when selling all shares
				# if portfolio_info.loc['Total', req[2]] < req[1] * stock_price :
				# 	portfolio_info.loc['Total', req[2]] = 0
				# else :
				# 	portfolio_info.loc['Total', req[2]] -= req[1] * stock_price
				if portfolio_info.loc['Parts', req[2]] == 0:
					portfolio_info.loc['Total', req[2]] = 0

			# the request is removed, with or without the user having enough shares
			del patched_list[i]
			request_list.remove(req)

		# If the request is not completed yet, pass to the next one.
		# If the request is completed, the request is removed from the list and
		# the next request is now at the current index.
		else:
			i += 1

	return patched_list,request_list, portfolio_info.to_dict(), cashflow


# Callback to delete items marked as done
@app.callback(
    Output("request-container", "children", allow_duplicate=True),
	Output("request-list", "data", allow_duplicate=True),
    Input("clear-done-btn", "n_clicks"),
    State({"index": ALL, "type": "done"}, "value"),
    prevent_initial_call=True,
)
def remove_request(n_clicks, state):
	patched_list = Patch()
	request_list = Patch()

	values_to_remove = []
	for i, val in enumerate(state):
		if val:
			values_to_remove.insert(0, i)
	for v in values_to_remove:
		del patched_list[v]
		del request_list[v]

	return patched_list, request_list
