from dash import callback, Input, Output, State, ALL, no_update, html, page_registry
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from trade.components.list import stock_list_element
from trade.utils.settings.create_market_data import delete_generated_data
from trade.defaults import defaults as dlt

@callback(
    Output("companies", "data"),
    Output("activities", "data"),
    Output("notifications", "children"),

    Input("add-company", "n_clicks"),

    State("input-stock", "value"),
    State("input-company", "value"),
    State("input-activity", "value"),
    State("companies", "data"),
    State("activities", "data"),
)
def add_company_and_activity(n, stock, company, activity, companies, activities):
    """
    Add a company and an activity to the stores
    Args:
        n: number of clicks
        stock: stock ticker
        company: company name
        activity: activity name
        companies: dictionary of companies
        activities: dictionary of activities
    Returns:
        companies: updated dictionary of companies
        activities: updated dictionary of activities
        notif: notification displayed
    """
    if not n:
        raise PreventUpdate

    if activity in activities.keys():
        # if activity exists, add stock to it
        activities[activity].append(stock)
    else:
        # if activity does not exist, create it and add stock to it
        activities[activity] = [stock]

    # add stock to companies
    companies[stock] = company

    # Success notification
    notif = dmc.Notification(
        id="notification-company-added",
        title="Company added",
        action="show",
        color="green",
        message=f"{company} has been added to the list of companies",
    )
    return companies, activities, notif


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
    return [stock_list_element(stock, company, lang) for stock, company in companies.items()]


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
    # join companies and indexes
    # TODO : handle indexes
    options = {**companies, **dlt.indexes}

    # if company not in options, select first company
    if company not in options.keys():
        company = list(options.keys())[0]

    # create options for selects
    options = [{"label": v, "value": k} for k, v in options.items()]

    return options, options, options, company


@callback(
    Output("list-companies", "children", allow_duplicate=True),
    Output("companies", "data", allow_duplicate=True),
    Output({"type": "delete-stock", "index": ALL}, "n_clicks"),

    Input({"type": "delete-stock", "index": ALL}, "n_clicks"),

    State("companies", "data"),
    State("list-companies", "children"),
    prevent_initial_call=True
)
def delete_companies(clicks, companies, children):
    """
    Delete a specific stock in the store and the csv file
    Args:
        clicks: list of clicks
        companies: dictionary of companies
        children: list of children displayed
    Returns:
        children: list of children displayed updated
        companies: dictionary of companies updated
        clicks: reset list of clicks
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

    clicks = [0] * len(clicks)  # reset all the clicks

    return children, companies, clicks


@callback(
    Output("input-activity", "data"),
    Input("activities", "data"),
    Input("settings-tabs", "value"),
)
def update_activities(data, tabs):
    """
    Update the activities select options
    Args:
        data: dictionary of activities
        tabs: current tab (used to update the callback)
    Returns:
        data: updated activities select options
    """
    data = [{"label": activity, "value": activity} for activity in list(data.keys())]
    return data


