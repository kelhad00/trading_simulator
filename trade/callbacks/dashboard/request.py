import pandas as pd

import dash_mantine_components as dmc
from dash import Output, Input, State, callback, no_update, page_registry as dash_registry, ALL
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.components.table import create_selectable_table
from trade.utils.market import get_price_dataframe


def add_request(req, company, action, price, share, cash, timestamp, port_shares):
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
    if len(req) == dlt.max_requests:
        return True, tls[dash_registry['lang']]["err-too-many-requests"]

    # If the form isn't filled correctly
    if price == 0:
        return True, tls[dash_registry['lang']]["err-wrong-form"]

    # If the request is to buy and the user doesn't have enough money
    stock_price = get_price_dataframe().loc[timestamp, company]
    if action == 'buy' and cash < share * stock_price:
        return True, tls[dash_registry['lang']]["err-enough-money"]

    # If the request is to sell and the user doesn't have enough shares
    port_shares = pd.DataFrame.from_dict(port_shares, orient='index', columns=['Shares'])
    if action == 'sell' and share > port_shares['Shares'].loc[company]:
        return True, tls[dash_registry['lang']]["err-enough-shares"].format(company)

    # Add the request to the list if no error
    req.append({
        'action': action,
        'shares': share,
        'company': company,
        'price': price
    })
    return False, req


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
    prevent_initial_call=True,
)
def process_submit_button(btn, company, action, price, share, cash, timestamp, port_shares, req):
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

    error, message = add_request(req, company, action, price, share, cash, timestamp, port_shares)

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

    State('timestamp', 'data'),
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
            if req['shares'] * req['price'] < cashflow:
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

    return request_list, port_shares['Shares'].to_dict(), cashflow, port_totals['Totals'].to_dict()


@callback(
    Output('request-table', 'children', allow_duplicate=True),
    Input("requests", "data"),
    prevent_initial_call=True
)
def cb_display_requests(req):
    """
       Create the table of the requests.
       Args:
           req: the list of requests
       Returns:
           dmc.Table: the table of the requests
       """

    df = pd.DataFrame(req)
    sell = tls[dash_registry['lang']]['request-action']['choices'][0]['label']
    buy = tls[dash_registry['lang']]['request-action']['choices'][1]['label']

    if not df.empty:
        # Replace all the 'buy' and 'sell' by their translated version
        df['action'] = df['action'].apply(lambda x: buy if x == 'buy' else sell)
        df.rename(columns={
            'action': tls[dash_registry['lang']]['requests-table']['actions'],
            'shares': tls[dash_registry['lang']]['requests-table']['shares'],
            'company': tls[dash_registry['lang']]['requests-table']['company'],
            'price': tls[dash_registry['lang']]['requests-table']['price']
        }, inplace=True)


    return dmc.Table(
        highlightOnHover=True,
        children=create_selectable_table(df, "requests-selectable-table"),
    )


@callback(
    Output('clear-done-btn', 'children'),
    Input({'type': 'requests-selectable-table', 'index': ALL}, 'checked')
)
def switch_label_delete_button(selected_rows):
    """
    Switch the label of the delete button.
    Between "Clear all requests" and "Clear requests".
    Args:
        selected_rows: the selected rows
    Returns:
        str: the label of the delete button
    """

    if len(selected_rows) == 0 or True not in selected_rows:
        return tls[dash_registry['lang']]["clear-all-requests-button"]
    else:
        return tls[dash_registry['lang']]["clear-requests-button"]


@callback(
    Output("requests", "data", allow_duplicate=True),
    Input('clear-done-btn', 'n_clicks'),
    State({'type': 'requests-selectable-table', 'index': ALL}, "checked"),
    State("requests", "data"),
    prevent_initial_call=True
)
def remove_request(n, values_to_remove, request_list):
    """
    Remove the selected requests.
    Args:
        n: the button nb click
        values_to_remove: the selected rows
        request_list: the list of requests
    Returns:
        request_list: the updated list of requests
    """
    if n is None or n == 0:
        raise PreventUpdate

    req = []
    if True in values_to_remove:
        for index, v in enumerate(values_to_remove):
            if v is not True:
                req.append(request_list[index])
    return req

