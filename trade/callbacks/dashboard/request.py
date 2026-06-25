import pandas as pd

import dash_mantine_components as dmc
from dash import Output, Input, State, callback, no_update, page_registry, ALL, ctx, html
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.components.table import create_table_delete
from trade.utils.market import get_price_dataframe


def add_request(req, company, action, price, share, cash, timestamp, port_shares, max_requests=dlt.max_requests):
    """
    Add a request to the list of requests.
    Args:
        req: the list of requests
        company: the company of the request
        action: the action of the request
        price: the price of the request
        share: the number of shares of the request
        cash: the money of the user
        timestamp: the current timestamp
        port_shares: the shares of the user
    Returns:
        boolean: is error ?
        msg: the error message or the updated list of requests
    """

    # If the user has too many requests
    if len(req) == max_requests:
        return True, tls[page_registry['lang']]["err-too-many-requests"]

    # If the form isn't filled correctly
    if price == 0:
        return True, tls[page_registry['lang']]["err-wrong-form"]

    # If the request is to buy and the user doesn't have enough money
    stock_price = get_price_dataframe().loc[timestamp, company]
    if action == 'buy' and cash < share * stock_price:
        return True, tls[page_registry['lang']]["err-enough-money"]

    # If the request is to sell and the user doesn't have enough shares
    port_shares = pd.DataFrame.from_dict(port_shares, orient='index', columns=['Shares'])
    if action == 'sell' and share > port_shares['Shares'].loc[company]:
        return True, tls[page_registry['lang']]["err-enough-shares"].format(company)

    # Add the request to the list if no error
    req.append({
        'action': action,
        'shares': share,
        'company': company,
        'price': price
    })
    return False, req


@callback(
    Output('price-input', 'value'),
    Input('company-graph', 'clickData'),
    State('company-selector', 'value'),
    prevent_initial_call=True,
)
def fill_price_from_candle_click(click_data, company):
    if not click_data or not company:
        raise PreventUpdate
    try:
        date_str = str(click_data['points'][0]['x'])[:10]
        price_df = get_price_dataframe()
        date_index = next(
            (idx for idx in price_df.index if str(idx)[:10] == date_str), None
        )
        if date_index is None:
            raise PreventUpdate
        return round(float(price_df.loc[date_index, company]), 4)
    except (KeyError, IndexError):
        raise PreventUpdate


@callback(
    Output("requests", "data", allow_duplicate=True),
    Output('notifications', 'children', allow_duplicate=True),

    Input("submit-button", "n_clicks"),

    State("company-selector", "value"),
    State("action-input", "value"),
    State("price-input", "value"),
    State("nbr-share-input", "value"),
    State('cashflow', 'data'),
    State('timestamp', 'data'),
    State('portfolio-shares', 'data'),
    State("requests", "data"),
    State("max-requests", "data"),
    prevent_initial_call=True,
)
def process_submit_button(btn, company, action, price, share, cash, timestamp, port_shares, req, max_requests):
    """
    Process the submit button.
    Add the request to the list of requests.
    Or return an error notification.
    Args:
        btn: the button nb click
        company: the company of the request
        action: the action of the request
        price: the price of the request
        share: the number of shares of the request
        cash: the money of the user
        timestamp: the current timestamp
        port_shares: the shares of the user
        req: the list of requests
    Returns:
        req: the updated list of requests
        dmc.Notification: the notification to display
    """

    if btn is None or btn == 0:
        raise PreventUpdate

    error, message = add_request(req, company, action, price, share, cash, timestamp, port_shares, max_requests)

    if error is True:
        return no_update, dmc.Notification(
            title="Error",
            id="simple-notify",
            action="show",
            color="red",
            icon=DashIconify(icon="material-symbols:error"),
            message=message,
        )
    else:
        # the request list has been returned
        req = message

    return req, no_update


@callback(
    Output("requests", "data", allow_duplicate=True),
    Output('portfolio-shares', 'data'),
    Output('cashflow', 'data'),
    Output('portfolio-totals', 'data'),

    Input("requests", "data"),
    Input('timestamp', 'data'),

    State('portfolio-shares', 'data'),
    State('cashflow', 'data'),
    State("portfolio-totals", "data"),
    prevent_initial_call=True,
)
def execute_requests(request_list, timestamp, port_shares, cashflow, port_totals):
    """
    Try to execute the requests of the user.
    Update the portfolio, the cashflow and requests list.
    Args:
        request_list: list of requests
        timestamp: current timestamp
        port_shares: dictionary of the shares of the user
        cashflow: the money of the user
        port_totals: dictionary of the total price of the user
    Returns:
        request_list: the updated list of requests
        port_shares: the updated dictionary of the shares of the user
        cashflow: the updated money of the user
        port_totals: the updated dictionary of the total price of the user
    """
    old_req = request_list.copy()

    price_list = get_price_dataframe()
    port_shares = pd.DataFrame.from_dict(port_shares, orient='index', columns=['Shares'])
    port_totals = pd.DataFrame.from_dict(port_totals, orient='index', columns=['Totals'])

    i = 0
    while i < len(request_list):
        req = request_list[i]
        stock_price = price_list.loc[timestamp, req['company']]

        # If the request is completed
        if req['action'] == 'buy' and req['price'] >= stock_price:
            # If the user has enough money
            if req['shares'] * req['price'] <= cashflow:
                # Update only the shares and the cashflow
                # Because the total price will be updated in the portfolio callback
                port_shares.loc[req['company']] += req['shares']
                cashflow -= req["shares"] * req["price"]

            # the request is removed, with or without the user having enough money
            request_list.remove(req)

        # Same as above for the sell request
        elif req['action'] == 'sell' and req['price'] <= stock_price:
            # If the user has enough shares
            if port_shares.at[req['company'], 'Shares'] >= req["shares"]:
                # Update only the shares and the cashflow
                # Because the total price will be updated in the portfolio callback
                port_shares.loc[req['company']] -= req["shares"]
                cashflow += req['shares'] * req['price']

            # the request is removed, with or without the user having enough shares
            request_list.remove(req)

        # If the request is not completed yet, pass to the next one.
        # If the request is completed, the request is removed from the list and
        # the next request is now at the current index.
        else:
            i += 1

    if not timestamp == "":
        # Update the total price of each stock
        port_totals['Totals'] = port_shares['Shares'] * price_list.loc[timestamp, port_totals.index]



    return request_list if old_req != request_list else no_update, port_shares['Shares'].to_dict(), cashflow, port_totals['Totals'].to_dict()


@callback(
    Output('request-table', 'children', allow_duplicate=True),
    Input("requests", "data"),
    prevent_initial_call=True
)
def cb_display_requests(req):
    lang = page_registry['lang']
    t = tls[lang]
    choices = t['request-action']['choices']

    header = html.Thead(html.Tr([
        html.Th(t['requests-table']['company']),
        html.Th(t['requests-table']['actions']),
        html.Th(t['requests-table']['price']),
        html.Th(t['requests-table']['shares']),
        html.Th(''),
    ]))

    if not req:
        rows = [html.Tr([html.Td('—', colSpan=5, style={"textAlign": "center", "color": "#aaa"})])]
    else:
        rows = []
        for i, r in enumerate(req):
            rows.append(html.Tr([
                html.Td(r['company'], style={"verticalAlign": "middle", "fontSize": "13px"}),
                html.Td(
                    dmc.SegmentedControl(
                        id={"type": "req-action-input", "index": i},
                        value=r['action'],
                        data=choices,
                        size="xs",
                    ),
                    style={"verticalAlign": "middle"},
                ),
                html.Td(
                    dmc.NumberInput(
                        id={"type": "req-price-input", "index": i},
                        value=r['price'],
                        min=0, step=0.001, precision=4,
                        size="xs",
                        style={"width": "90px"},
                    ),
                    style={"verticalAlign": "middle"},
                ),
                html.Td(
                    dmc.NumberInput(
                        id={"type": "req-shares-input", "index": i},
                        value=r['shares'],
                        min=1, step=1,
                        size="xs",
                        style={"width": "70px"},
                    ),
                    style={"verticalAlign": "middle"},
                ),
                html.Td(
                    dmc.ActionIcon(
                        DashIconify(icon="material-symbols:delete-outline", width=20),
                        size="md", radius="md", color="dark", variant="outline",
                        id={"type": "requests-selectable-table", "index": i},
                    ),
                    style={"verticalAlign": "middle"},
                ),
            ]))

    return dmc.Table(
        highlightOnHover=True,
        children=[header, html.Tbody(rows)],
    )


@callback(
    Output('requests', 'data', allow_duplicate=True),
    Input({'type': 'req-price-input', 'index': ALL}, 'value'),
    Input({'type': 'req-shares-input', 'index': ALL}, 'value'),
    Input({'type': 'req-action-input', 'index': ALL}, 'value'),
    State('requests', 'data'),
    prevent_initial_call=True,
)
def edit_request_values(prices, shares, actions, requests):
    if not requests:
        raise PreventUpdate

    changed = False
    for i, (price, share, action) in enumerate(zip(prices, shares, actions)):
        if i >= len(requests):
            break
        if price is not None and requests[i]['price'] != price:
            requests[i]['price'] = price
            changed = True
        if share is not None and requests[i]['shares'] != share:
            requests[i]['shares'] = share
            changed = True
        if action is not None and requests[i]['action'] != action:
            requests[i]['action'] = action
            changed = True

    return requests if changed else no_update

@callback(
    Output("requests", "data", allow_duplicate=True),
    Input('clear-done-btn', 'n_clicks'),
    Input({'type': 'requests-selectable-table', 'index': ALL}, "n_clicks"),
    State("requests", "data"),
    prevent_initial_call=True
)
def remove_request(n, values_to_remove, req):
    """
    Remove the selected requests.
    Args:
        n: the button nb click
        values_to_remove: the selected rows
        request_list: the list of requests
    Returns:
        request_list: the updated list of requests
        list: reset the nb of clicks of each delete button
    """

    if ctx.triggered_id == 'clear-done-btn':
        return []
    else:
        if 1 in values_to_remove:
            index = values_to_remove.index(1)
            del req[index]
            return req
        else:
            return no_update

