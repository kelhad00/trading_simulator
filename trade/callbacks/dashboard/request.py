import time

import pandas as pd

import dash_mantine_components as dmc
from dash import Output, Input, State, html, callback, no_update, page_registry as dash_registry, Patch, ALL, ctx
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.utils.create_table import create_table, create_selectable_table
from trade.utils.market import get_price_dataframe
from trade.utils.store.export import export_data


# ==========Request callbacks==========

def exec_request(request_list,  timestamp, port_shares, cashflow, port_totals):
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




def get_request_table(df):
    sell = tls[dash_registry['lang']]['request-action']['choices'][0]['label']
    buy = tls[dash_registry['lang']]['request-action']['choices'][1]['label']

    if not df.empty:
        # replace all the 'buy' and 'sell' by their translated version
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


def update_requests(req, company, action, price, share, cash, timestamp, port_shares):

    # If the user has too many requests
    if len(req) == dlt.max_requests:
        return True, tls[dash_registry['lang']]["err-too-many-requests"]

    # If the form isn't filled correctly
    if price == 0:
        return True, tls[dash_registry['lang']]["err-wrong-form"]

    stock_price = get_price_dataframe().loc[timestamp, company]
    # If the request is to buy and the user doesn't have enough money
    if action == 'buy' and cash < share * stock_price:
        return True, tls[dash_registry['lang']]["err-enough-money"]

    port_shares = pd.DataFrame.from_dict(port_shares, orient='index', columns=['Shares'])
    # If the request is to sell and the user doesn't have enough shares
    if action == 'sell' and share > port_shares['Shares'].loc[company]:
        return True, tls[dash_registry['lang']]["err-enough-shares"].format(company)

    req.append({
        'action': action,
        'shares': share,
        'company': company,
        'price': price
    })
    return False, req


def process_submit_button(company, action, price, share, cash, timestamp, port_shares, req):
    # get error message or the request list updated
    error, message = update_requests(req, company, action, price, share, cash, timestamp, port_shares)

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
    Output("requests", "data"),
    Output('notifications', 'children', allow_duplicate=True),
    Output('request-table', 'children', allow_duplicate=True),
    Output('portfolio-shares', 'data'),
    Output('cashflow', 'data'),
    Output('portfolio-totals', 'data'),

    Input("submit-button", "n_clicks"),
    Input("periodic-updater", "n_intervals"),

    State("company-selector", "value"),
    State("action-input", "value"),
    State("price-input", "value"),
    State("nbr-share-input", "value"),
    State('cashflow', 'data'),
    State('timestamp', 'data'),
    State('portfolio-shares', 'data'),
    State("requests", "data"),
    State("portfolio-totals", "data"),

    #only used for export data
    State('description-title', 'children'),
    State('segmented', "value"),
    prevent_initial_call=True,
)
def request_handler(btn, n, company, action, price, share, cash, timestamp, port_shares, req, port_totals, news_title, graph_choice):

    if ctx.triggered_id == 'submit-button':
        req, notification = process_submit_button(company, action, price, share, cash, timestamp, port_shares, req)
        if notification is not no_update:
            return no_update, notification, no_update, no_update, no_update, no_update
        export_data(timestamp, req, cash, port_shares, port_totals, company, news_title, graph_choice, action)

    req, port_shares, cash, port_totals = exec_request(req, timestamp, port_shares, cash, port_totals)
    df = pd.DataFrame(req)
    table = get_request_table(df)
    export_data(timestamp, req, cash, port_shares, port_totals, company, news_title, graph_choice, action)
    return req, no_update, table, port_shares, cash, port_totals





@callback(
    Output("request-table", "children"),
    Input("periodic-updater", "n_intervals"),
    State("requests", "data"),
)
def cb_display_requests(n, req):
    df = pd.DataFrame(req)
    return get_request_table(df)


@callback(
    Output('clear-done-btn', 'children'),
    Input({'type': 'requests-selectable-table', 'index': ALL}, 'checked')
)
def cb_switch_between_delete_and_delete_all(selected_rows):
    if len(selected_rows) == 0:
        return tls[dash_registry['lang']]["clear-all-requests-button"]
    elif True not in selected_rows:
        return tls[dash_registry['lang']]["clear-all-requests-button"]
    else:
        return tls[dash_registry['lang']]["clear-requests-button"]





@callback(
    Output("requests", "data", allow_duplicate=True),
    Output('request-table', 'children', allow_duplicate=True),

    Input('clear-done-btn', 'n_clicks'),

    State({'type': 'requests-selectable-table', 'index': ALL}, "checked"),
    State("requests", "data"),

    #only used for export data
    State("company-selector", "value"),
    State("action-input", "value"),
    State('cashflow', 'data'),
    State('timestamp', 'data'),
    State('portfolio-shares', 'data'),
    State("portfolio-totals", "data"),
    State('description-title', 'children'),
    State('segmented', "value"),

    prevent_initial_call=True
)
def cb_remove_request(n, values_to_remove, request_list, company, action, cash, timestamp, port_shares, port_totals, news_title, graph_choice):
    if n is None:
        raise PreventUpdate  # Avoid callback to be triggered at the first load

    if not True in values_to_remove:
        req = []

    else:  # Remove the selected requests
        req = []
        for index, v in enumerate(values_to_remove):
            if v is not True:
                req.append(request_list[index])

    df = pd.DataFrame(req)
    table = get_request_table(df)

    export_data(timestamp, req, cash, port_shares, port_totals, company, news_title, graph_choice, action, values_to_remove)

    return req, table


def count_rows_in_table(table):
    # Parcourir les enfants de l'objet table
    for child in table['props']['children']:
        # Vérifier si l'enfant est le 'Tbody' du tableau
        if child['type'] == 'Tbody':
            # Retourner le nombre de lignes dans le 'Tbody'
            return len(child['props']['children'])
    # Retourner 0 si aucun 'Tbody' n'est trouvé
    return 0


@callback(
    Output("price-input", "disabled"),
    Output("nbr-share-input", "disabled"),
    Output("submit-button", "disabled"),
    Input("company-selector", "value"),
)
def cb_change_state_request_form(company):
    """ Disable the request form when an index is selected
    And enable it want a company is selected
    """
    if company in dlt.indexes.keys():
        return True, True, True  # Disable the form
    else:
        return False, False, False  # Enable the form



