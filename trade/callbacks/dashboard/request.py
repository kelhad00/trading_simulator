import pandas as pd

import dash_mantine_components as dmc
from dash import Output, Input, State, callback, no_update, page_registry, ALL, ctx, html, clientside_callback
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from trade.defaults import defaults as dlt
from trade.locales import translations as tls
from trade.components.table import create_table_delete
from trade.utils.market import get_price_dataframe, get_low_dataframe, get_high_dataframe


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
        return True, tls[page_registry.get('lang', 'fr')]["err-too-many-requests"]

    # If the form isn't filled correctly
    if price == 0:
        return True, tls[page_registry.get('lang', 'fr')]["err-wrong-form"]

    # If the request is to buy and the user doesn't have enough money
    stock_price = get_price_dataframe().loc[timestamp, company]
    if action == 'buy' and cash < share * stock_price:
        return True, tls[page_registry.get('lang', 'fr')]["err-enough-money"]

    # If the request is to sell and the user doesn't have enough shares
    port_shares = pd.DataFrame.from_dict(port_shares, orient='index', columns=['Shares'])
    if action == 'sell' and share > port_shares['Shares'].loc[company]:
        return True, tls[page_registry.get('lang', 'fr')]["err-enough-shares"].format(company)

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
        return round(float(price_df.loc[date_index, company]), 2)
    except (KeyError, IndexError):
        raise PreventUpdate


@callback(
    Output('price-input', 'value', allow_duplicate=True),
    Input('market-price-btn', 'n_clicks'),
    State('company-selector', 'value'),
    State('timestamp', 'data'),
    prevent_initial_call=True,
)
def fill_market_price(n_clicks, company, timestamp):
    if not n_clicks or not company or not timestamp:
        raise PreventUpdate
    price = get_price_dataframe().loc[timestamp, company]
    return round(float(price), 2)


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
    low_list   = get_low_dataframe()
    high_list  = get_high_dataframe()
    port_shares = pd.DataFrame.from_dict(port_shares, orient='index', columns=['Shares'])
    port_totals = pd.DataFrame.from_dict(port_totals, orient='index', columns=['Totals'])

    i = 0
    while i < len(request_list):
        req = request_list[i]
        low_price  = low_list.loc[timestamp, req['company']]
        high_price = high_list.loc[timestamp, req['company']]

        # If the request is completed
        if req['action'] == 'buy' and low_price <= req['price']:
            # If the user has enough money
            if req['shares'] * req['price'] <= cashflow:
                # Update only the shares and the cashflow
                # Because the total price will be updated in the portfolio callback
                port_shares.loc[req['company']] += req['shares']
                cashflow -= req["shares"] * req["price"]

            # the request is removed, with or without the user having enough money
            request_list.remove(req)

        # Same as above for the sell request
        elif req['action'] == 'sell' and high_price >= req['price']:
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
    Input('lang', 'data'),
    State('portfolio-shares', 'data'),
    State('cashflow', 'data'),
    prevent_initial_call='initial_duplicate'
)
def cb_display_requests(req, lang, port_shares, cashflow):
    lang = lang or page_registry.get('lang', 'fr')
    t = tls[lang]
    choices = t['request-action']['choices']
    port_shares = port_shares or {}
    cashflow = cashflow or 0

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
            if r['action'] == 'sell':
                max_shares = int(port_shares.get(r['company'], 0)) or None
            else:
                price = r.get('price', 0)
                max_shares = int(cashflow // price) if price > 0 else None

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
                        min=0, step=0.01, precision=2,
                        size="xs",
                        style={"width": "90px"},
                    ),
                    style={"verticalAlign": "middle"},
                ),
                html.Td(
                    dmc.NumberInput(
                        id={"type": "req-shares-input", "index": i},
                        value=r['shares'],
                        min=1, max=max_shares, step=1,
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
    State('portfolio-shares', 'data'),
    State('cashflow', 'data'),
    prevent_initial_call=True,
)
def edit_request_values(prices, shares, actions, requests, port_shares, cashflow):
    if not requests:
        raise PreventUpdate

    port_shares = port_shares or {}
    cashflow = cashflow or 0

    changed = False
    for i, (price, share, action) in enumerate(zip(prices, shares, actions)):
        if i >= len(requests):
            break

        # Use the updated values where available, otherwise fall back to stored values
        eff_action = action if action is not None else requests[i]['action']
        eff_price = price if price is not None else requests[i]['price']
        company = requests[i]['company']

        if price is not None and requests[i]['price'] != price:
            requests[i]['price'] = price
            changed = True
        if action is not None and requests[i]['action'] != action:
            requests[i]['action'] = action
            changed = True
        if share is not None:
            if eff_action == 'sell':
                max_shares = int(port_shares.get(company, 0)) or None
            else:
                max_shares = int(cashflow // eff_price) if eff_price > 0 else None
            clamped = max(1, min(share, max_shares)) if max_shares else max(1, share)
            if requests[i]['shares'] != clamped:
                requests[i]['shares'] = clamped
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
        if not n:
            raise PreventUpdate
        return []
    else:
        if 1 in values_to_remove:
            index = values_to_remove.index(1)
            del req[index]
            return req
        else:
            return no_update


# ── Right-click context menu on chart ─────────────────────────────────────────

# 1. Set up the contextmenu listener each time the figure renders
clientside_callback(
    """function(figure) {
        window._ctxPrice = window._ctxPrice || 0;

        function attach() {
            var outer = document.getElementById('company-graph');
            if (!outer) { setTimeout(attach, 300); return; }
            if (outer._ctxAttached) return;
            outer._ctxAttached = true;

            outer.addEventListener('contextmenu', function(e) {
                e.preventDefault();

                // The Plotly graph element (has _fullLayout) is the inner .js-plotly-plot div
                var plotlyDiv = outer.querySelector('.js-plotly-plot') || outer;
                if (plotlyDiv._fullLayout) {
                    var yaxis     = plotlyDiv._fullLayout.yaxis;
                    var rect      = plotlyDiv.getBoundingClientRect();
                    var plotTop   = rect.top + plotlyDiv._fullLayout.margin.t;
                    var yFraction = (e.clientY - plotTop) / (yaxis._length || 1);
                    var yRange    = yaxis.range;
                    var yData     = yRange[1] - yFraction * (yRange[1] - yRange[0]);
                    window._ctxPrice = Math.round(Math.max(0, yData) * 100) / 100;
                }

                var menu = document.getElementById('chart-context-menu');
                if (menu) {
                    menu.style.display = 'flex';
                    menu.style.left = (e.clientX + 4) + 'px';
                    menu.style.top  = (e.clientY + 4) + 'px';
                }
            });

            outer.addEventListener('click', function(e) {
                var plotlyDiv = outer.querySelector('.js-plotly-plot') || outer;
                if (plotlyDiv._fullLayout) {
                    var yaxis     = plotlyDiv._fullLayout.yaxis;
                    var rect      = plotlyDiv.getBoundingClientRect();
                    var plotTop   = rect.top + plotlyDiv._fullLayout.margin.t;
                    var yFraction = (e.clientY - plotTop) / (yaxis._length || 1);
                    var yRange    = yaxis.range;
                    var yData     = yRange[1] - yFraction * (yRange[1] - yRange[0]);
                    window._leftClickPrice = Math.round(Math.max(0, yData) * 100) / 100;
                    var trigger = document.getElementById('ctx-left-click-trigger');
                    if (trigger) trigger.click();
                }
            });

            document.addEventListener('click', function(e) {
                var menu = document.getElementById('chart-context-menu');
                if (menu && !menu.contains(e.target)) {
                    menu.style.display = 'none';
                }
            }, {once: false});
        }
        setTimeout(attach, 200);
        return window.dash_clientside.no_update;
    }""",
    Output('ctx-setup-done', 'data'),
    Input('company-graph', 'figure'),
)

# 2. Buy here button → store price + action
clientside_callback(
    """function(n) {
        if (!n) return window.dash_clientside.no_update;
        document.getElementById('chart-context-menu').style.display = 'none';
        return {price: window._ctxPrice || 0, action: 'buy'};
    }""",
    Output('ctx-right-click', 'data'),
    Input('ctx-buy-btn', 'n_clicks'),
)

# 3. Sell here button → store price + action
clientside_callback(
    """function(n) {
        if (!n) return window.dash_clientside.no_update;
        document.getElementById('chart-context-menu').style.display = 'none';
        return {price: window._ctxPrice || 0, action: 'sell'};
    }""",
    Output('ctx-right-click', 'data', allow_duplicate=True),
    Input('ctx-sell-btn', 'n_clicks'),
    prevent_initial_call=True,
)

clientside_callback(
    """function(n) {
        if (!n) return window.dash_clientside.no_update;
        return {price: window._leftClickPrice || 0};
    }""",
    Output('ctx-left-click', 'data'),
    Input('ctx-left-click-trigger', 'n_clicks'),
  )

clientside_callback(
    """function(data) {
        if (!data || !data.price) return window.dash_clientside.no_update;
        return data.price;
    }""",
    Output('price-input', 'value', allow_duplicate=True),
    Input('ctx-left-click', 'data'),
    prevent_initial_call=True,
  )

# 4. Apply right-click selection to the request form
@callback(
    Output('price-input', 'value', allow_duplicate=True),
    Output('action-input', 'value'),
    Input('ctx-right-click', 'data'),
    prevent_initial_call=True,
)
def apply_context_price(data):
    if not data or data.get('price') is None:
        raise PreventUpdate
    return data['price'], data['action']

