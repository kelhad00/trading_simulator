import pandas as pd

import dash_mantine_components as dmc
from dash import Output, Input, State, callback, no_update, page_registry, ALL, ctx
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.components.table import create_table_delete
from trade.utils.market import get_price_dataframe, format_timestamp


def add_request(req, company, action, price, share, cash, timestamp, port_shares, max_requests=dlt.max_requests):
    """Validate and append a new buy/sell request to the pending list.

    Args:
        req (list): Existing requests.
        company (str): Target company ticker.
        action (str): 'buy' or 'sell'.
        price (float): Limit price.
        share (int): Number of shares.
        cash (float): Available cash.
        timestamp: Current timestamp (unused here, for future checks).
        port_shares (dict): Current portfolio shares.
        max_requests (int): Maximum allowed pending requests.

    Returns:
        tuple[bool, str|list]: (is_error, message_or_updated_requests)
    """

    # If the user has too many requests
    if len(req) == max_requests:
        return True, tls[page_registry['lang']]["err-too-many-requests"]

    # If the form isn't filled correctly
    if price == 0:
        return True, tls[page_registry['lang']]["err-wrong-form"]

    # If the request is to buy and the user doesn't have enough money
    if action == 'buy' and cash < share * price:
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
    """Handle submit action to create a new request or show an error.

    Args:
        btn (int): Clicks on submit.
        company (str): Company ticker.
        action (str): 'buy' or 'sell'.
        price (float): Limit price.
        share (int): Number of shares.
        cash (float): Available cash.
        timestamp: Current timestamp.
        port_shares (dict): Current shares by symbol.
        req (list): Existing requests.
        max_requests (int): Max allowed requests.

    Returns:
        tuple: (updated requests or no_update, notification or no_update)
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
    """Attempt to execute pending requests at current market prices.

    Args:
        request_list (list): Pending requests.
        timestamp (str|pd.Timestamp): Current timestamp.
        port_shares (dict): Current shares by symbol.
        cashflow (float): Available cash.
        port_totals (dict): Totals by symbol.

    Returns:
        tuple: (updated requests or no_update, shares dict, cashflow, totals dict)
    """
    old_req = request_list.copy()

    timestamp = pd.to_datetime(timestamp)

    timestamp = format_timestamp(timestamp)

    price_list = get_price_dataframe()
    port_shares = pd.DataFrame.from_dict(port_shares, orient='index', columns=['Shares'])
    port_totals = pd.DataFrame.from_dict(port_totals, orient='index', columns=['Totals'])
    
    # Ensure numeric types
    port_shares['Shares'] = pd.to_numeric(port_shares['Shares'], errors='coerce')
    port_totals['Totals'] = pd.to_numeric(port_totals['Totals'], errors='coerce')
    port_shares['Shares'] = port_shares['Shares'].fillna(0)
    port_totals['Totals'] = port_totals['Totals'].fillna(0)

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

    if not timestamp == "" and timestamp in price_list.index:
        # Update the total price of each stock
        port_totals['Totals'] = port_shares['Shares'] * price_list.loc[timestamp, port_totals.index]



    return request_list if old_req != request_list else no_update, port_shares['Shares'].to_dict(), cashflow, port_totals['Totals'].to_dict()


@callback(
    Output('request-table', 'children', allow_duplicate=True),
    Input("requests", "data"),
    prevent_initial_call=True
)
def cb_display_requests(req):
    """Render the requests list into a selectable table.

    Args:
        req (list): Current requests.

    Returns:
        dmc.Table: Table with delete buttons for each row.
    """

    df = pd.DataFrame(req)
    sell = tls[page_registry['lang']]['request-action']['choices'][0]['label']
    buy = tls[page_registry['lang']]['request-action']['choices'][1]['label']

    if not df.empty:
        # Replace all the 'buy' and 'sell' by their translated version
        df['action'] = df['action'].apply(lambda x: buy if x == 'buy' else sell)
        df.rename(columns={
            'action': tls[page_registry['lang']]['requests-table']['actions'],
            'shares': tls[page_registry['lang']]['requests-table']['shares'],
            'company': tls[page_registry['lang']]['requests-table']['company'],
            'price': tls[page_registry['lang']]['requests-table']['price']
        }, inplace=True)


    return dmc.Table(
        highlightOnHover=True,
        children=create_table_delete(df, "requests-selectable-table"),
    )

@callback(
    Output("requests", "data", allow_duplicate=True),
    Input('clear-done-btn', 'n_clicks'),
    Input({'type': 'requests-selectable-table', 'index': ALL}, "n_clicks"),
    State("requests", "data"),
    prevent_initial_call=True
)
def remove_request(n, values_to_remove, req):
    """Remove selected requests or clear all completed ones.

    Args:
        n (int): Clicks on the clear-all button.
        values_to_remove (list[int|None]): Per-row delete clicks.
        req (list): Current requests list.

    Returns:
        list|no_update: Updated requests list or no_update.
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

@callback(
    Output("submit-button", "children"),
    Input("price-input", "value"),
    Input("nbr-share-input", "value"),
)
def total_cost(price,nb):
    """Display total estimated cost on the submit button label.

    Args:
        price (float|None): Limit price.
        nb (int|None): Number of shares.

    Returns:
        str: Label including total cost when possible.
    """
    if price == 0 or nb == 0 or price == "" or nb == "" or price is None or nb is None:
        return tls[page_registry['lang']]['submit-request']
    else:
        return f" {tls[page_registry['lang']]['submit-request']} - Total : {price * nb}€"

@callback(
    Output("nbr-share-input", "value"),
    Input("max-share-button", "n_clicks"),
    State("price-input", "value"),
    State("cashflow","data"),
    State("action-input", "value"),
    State("company-selector", "value"),
    State('portfolio-shares', 'data'),
    prevent_initial_call=True
)
def max_share(btn,price,cashflow,action,company,portfolio):
    """Compute the maximum shares purchasable/sellable based on context.

    Args:
        btn (int): Clicks on max-share button (unused, triggers only).
        price (float|None): Current limit price.
        cashflow (float|None): Available cash.
        action (str): 'buy' or 'sell'.
        company (str): Target company ticker.
        portfolio (dict): Current shares by symbol.

    Returns:
        int|no_update: Suggested number of shares or no_update when not applicable.
    """

    if action == "buy":

        # Ensure price and cashflow are numeric and not NaN
        try:
            price = float(price) if price is not None else 0
            cashflow = float(cashflow) if cashflow is not None else 0
            
            if price > 0 and cashflow > 0:
                return int(cashflow/price)
            else:
                return no_update
        except (ValueError, TypeError):
            return no_update
    else:
        portfolio = pd.DataFrame.from_dict(portfolio, orient='index', columns=['Shares'])
        # Ensure numeric type
        portfolio['Shares'] = pd.to_numeric(portfolio['Shares'], errors='coerce')
        portfolio['Shares'] = portfolio['Shares'].fillna(0)
        
        if portfolio['Shares'].loc[company] != 0:
            return int(portfolio['Shares'].loc[company])
        else:
            return no_update