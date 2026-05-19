from dash import callback, Input, Output, State, ALL, MATCH, no_update, html, page_registry
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from trade.components.list import stock_list_element
from trade.locales import translations as tls
from trade.utils.settings.create_market_data import delete_generated_data, get_generated_data
from trade.defaults import defaults as dlt


@callback(
    Output("companies", "data"),
    Output("notifications", "children"),
    Output("input-stock", "value"),
    Output("input-company", "value"),
    Output("input-activity", "value"),
    Output("input-description", "value"),

    Input("add-company", "n_clicks"),

    State("input-stock", "value"),
    State("input-company", "value"),
    State("input-activity", "value"),
    State("input-description", "value"),
    State("companies", "data"),
    prevent_initial_call=True
)
def add_company_and_activity(n, stock, company, activity, description, companies):
    """
    Add a company and an activity to the stores
    Args:
        n: number of clicks
        stock: stock ticker
        company: company name
        activity: activity name
        companies: dictionary of companies
    Returns:
        companies: updated dictionary of companies
        notif: notification displayed
    """
    if not n:
        raise PreventUpdate

    # add stock to companies
    companies[stock] = {
        "label": company,
        "activity": activity,
        "got_charts": False,
        "description": description or "",
    }

    # Success notification
    notif = dmc.Notification(
        id="notification-company-added",
        title="Company added",
        action="show",
        color="green",
        message=f"{company} has been added to the list of companies",
    )

    return companies, notif, "", None, None, ""


@callback(
    Output("list-companies", "children"),
    Input("companies", "data"),
    Input("settings-tabs", "value")
)
def display_companies(companies, tabs):
    """
    Display the list of companies in the stocks tab
    Args:
        companies: dictionary of companies
        tabs: current tab (used to update the callback)
    Returns:
        list of companies displayed
    """
    lang = page_registry["lang"]
    return [stock_list_element(stock, company["label"], lang) for stock, company in companies.items()]


@callback(
    Output("select-company", "data"),  # select company in charts tab
    Output("modal-select-companies", "data"),  # select company in charts modal tab
    Output("input-company", "data"),  # input selectable company in stocks tab
    Output("select-company", "value"),

    Input("companies", "data"),
    Input("settings-tabs", "value"),

    State("select-company", "value"),
)
def update_select_company_options(companies, tabs, company):
    options = companies

    # if company not in options, select first company
    if company not in options.keys():
        company = list(options.keys())[0]

    # create options for selects
    options = [{"label": v["label"], "value": k} for k, v in options.items()]

    return options, options, options, company


@callback(
    Output("companies", "data", allow_duplicate=True),
    Input("settings-tabs", "value"),
    State("companies", "data"),
    prevent_initial_call=True
)
def update_companies(tabs, companies):
    """
    Update the companies select options
    Args:
        tabs: current tab (used to update the callback)
        companies: dictionary of companies
    Returns:
        data: updated companies select options
    """
    df = get_generated_data()  # Get the data of all companies
    df_companies = df.columns.get_level_values('symbol').unique()  # Get the list of companies in the csv file

    # Get the intersection between the companies in the csv file and the companies in the store
    intersection = list(set(df_companies) & set(companies))
    for company in intersection:
        # Update the got_charts value of the companies in the store
        companies[company]['got_charts'] = True

    return companies


@callback(
    Output("companies", "data", allow_duplicate=True),
    Input("reset-stocks", "n_clicks"),
    prevent_initial_call=True
)
def reset_stocks(n):
    """ Reset the companies list with the default companies """
    df = get_generated_data()  # Get the data of all companies
    df_companies = df.columns.get_level_values('symbol').unique()  # Get the list of companies in the csv file
    companies = dlt.companies_list

    for company in companies:
        if company not in df_companies:  # check if there is no data for the company
            companies[company]['got_charts'] = False

    return companies


@callback(
    Output("portfolio-shares", "data", allow_duplicate=True),
    Output("portfolio-totals", "data", allow_duplicate=True),
    Input("companies", "data"),
    prevent_initial_call=True
)
def update_portfolio(companies):
    """
    Update the portfolio shares and totals
    Args:
        companies: dictionary of companies
    Returns:
        portfolio_shares: updated portfolio shares
        portfolio_totals: updated portfolio totals
    """
    value = {stock: 0 for stock, company in companies.items() if company["got_charts"]}
    return value, value


@callback(
    Output("list-companies", "children", allow_duplicate=True),
    Output("companies", "data", allow_duplicate=True),
    Output({"type": "delete-stock", "index": ALL}, "n_clicks"),
    Output("portfolio-shares", "data", allow_duplicate=True),
    Output("portfolio-totals", "data", allow_duplicate=True),

    Input({"type": "delete-stock", "index": ALL}, "n_clicks"),

    State("companies", "data"),
    State("list-companies", "children"),
    State("portfolio-shares", "data"),
    State("portfolio-totals", "data"),
    prevent_initial_call=True
)
def delete_companies(clicks, companies, children, portfolio_shares, portfolio_totals):
    """
    Delete a specific stock in the store and the csv file
    Args:
        clicks: list of clicks
        companies: dictionary of companies
        children: list of children displayed
        portfolio_shares: dictionary of portfolio shares
        portfolio_totals: dictionary of portfolio totals
    Returns:
        children: list of children displayed updated
        companies: dictionary of companies updated
        clicks: reset list of clicks
        portfolio_shares: dictionary of portfolio shares updated
        portfolio_totals: dictionary of portfolio totals updated
    """

    if not clicks or not 1 in clicks:
        raise PreventUpdate

    # Get all the children that have not been clicked
    children = [child for index, child in enumerate(children) if not clicks[index]]

    if 1 in clicks:
        # Get the index of the clicked child
        index = clicks.index(1)

        # Get the key of the clicked child in the companies dictionary
        stock = list(companies.keys())[index]

        # Delete the stock from the companies dictionary and the csv file
        del companies[stock]
        delete_generated_data(stock)

        # Delete the stock from the portfolio
        try:
            del portfolio_shares[stock]
            del portfolio_totals[stock]
        except:
            # if the stock is not in the portfolio, pass
            pass

    clicks = [0] * len(clicks)  # reset all the clicks

    return children, companies, clicks, portfolio_shares, portfolio_totals


@callback(
    Output("input-activity", "data"),
    Input("companies", "data"),
    Input("settings-tabs", "value"),
)
def update_activities(companies, tabs):
    """
    Update the activities select options
    Args:
        companies: all the companies with an activity field for each
        tabs: current tab (used to update the callback)
    Returns:
        data: updated activities select options
    """
    # get all the unique activities in companies dictionary
    activities = list(set([company["activity"] for company in companies.values()]))
    data = [{"label": activity, "value": activity} for activity in activities]
    return data


# ── Inline label editing ──────────────────────────────────────────────────────

@callback(
    Output({"type": "company-name-text", "index": MATCH}, "style"),
    Output({"type": "edit-stock-input", "index": MATCH}, "style"),
    Output({"type": "edit-stock", "index": MATCH}, "style"),
    Output({"type": "save-stock", "index": MATCH}, "style"),
    Input({"type": "edit-stock", "index": MATCH}, "n_clicks"),
)
def enter_edit_mode(n):
    """Switch a single company row from read-only to edit mode."""
    if not n:
        raise PreventUpdate
    return (
        {"display": "none"},   # hide the plain-text label
        {"display": "block"},  # show the text input
        {"display": "none"},   # hide the Edit button
        {"display": "flex"},   # show the Save button
    )


@callback(
    Output("companies", "data", allow_duplicate=True),
    Output("notifications", "children", allow_duplicate=True),
    Input({"type": "save-stock", "index": ALL}, "n_clicks"),
    State({"type": "edit-stock-input", "index": ALL}, "value"),
    State("companies", "data"),
    prevent_initial_call=True,
)
def save_company_label(clicks, new_labels, companies):
    """
    Persist the edited company label to the companies store.

    After this callback updates the store, display_companies re-renders the
    entire list — every row returns to read-only mode automatically.
    """
    if not clicks or not any(clicks):
        raise PreventUpdate

    index = next((i for i, c in enumerate(clicks) if c), None)
    if index is None:
        raise PreventUpdate

    ticker = list(companies.keys())[index]
    new_label = new_labels[index] if index < len(new_labels) else None

    lang = page_registry.get("lang", "fr")
    tl = tls[lang]["settings"]["tickers"]["notification"]

    if not new_label or not new_label.strip():
        notif = dmc.Notification(
            id="notif-label-error",
            title=tl["error-title"],
            message=tl["error-msg"],
            color="red",
            action="show",
            autoClose=4000,
        )
        return no_update, notif

    companies[ticker]["label"] = new_label.strip()

    notif = dmc.Notification(
        id="notif-label-saved",
        title=tl["success-title"],
        message=tl["success-msg"].format(ticker=ticker, name=new_label.strip()),
        color="green",
        action="show",
        autoClose=3000,
    )

    return companies, notif
