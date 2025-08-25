from dash import callback, Input, Output, State, ALL, no_update, html, page_registry
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from trade.components.list import stock_list_element
from trade.utils.settings.create_market_data import delete_generated_data, get_generated_data
from trade.defaults import defaults as dlt


@callback(
    Output("companies", "data"),
    Output("notifications", "children"),

    Input("add-company", "n_clicks"),

    State("input-stock", "value"),
    State("input-company", "value"),
    State("input-activity", "value"),
    State("companies", "data"),
    prevent_initial_call=True
)
def add_company_and_activity(n, stock, company, activity, companies):
    """Add a new company with activity to the store and notify success.

    Args:
        n (int): Clicks on add button.
        stock (str): Ticker symbol.
        company (str): Display label.
        activity (str): Sector/activity name.
        companies (dict): Current companies store.

    Returns:
        tuple: (updated companies dict, success notification)
    """
    if not n:
        raise PreventUpdate

    # add stock to companies
    companies[stock] = {
        "label": company,
        "activity": activity,
        "got_charts": False,
    }

    # Success notification
    notif = dmc.Notification(
        id="notification-company-added",
        title="Company added",
        action="show",
        color="green",
        message=f"{company} has been added to the list of companies",
    )

    return companies, notif


@callback(
    Output("list-companies", "children"),
    Input("companies", "data"),
    Input("settings-tabs", "value")
)
def display_companies(companies, tabs):
    """Render list of companies for the stocks tab.

    Args:
        companies (dict): Companies store.
        tabs (str): Current tab id (trigger only).

    Returns:
        list: Rendered list elements.
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
    """Update companies options for various selects and maintain value.

    Args:
        companies (dict): Companies store.
        tabs (str): Current tab id (trigger only).
        company (str|None): Currently selected ticker.

    Returns:
        tuple[list, list, list, str]: Options for selects and the ensured selected value.
    """
    # join companies and indexes
    # TODO : handle indexes
    # options = {**companies, **dlt.indexes}
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
    """Mark companies as having charts when data exists in generated_data.csv.

    Args:
        tabs (str): Current tab id (trigger only).
        companies (dict): Companies store.

    Returns:
        dict: Updated companies store.
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
    """Reset the companies list to defaults while preserving got_charts flags.

    Args:
        n (int): Clicks on reset.

    Returns:
        dict: Reset companies store.
    """
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
    """Initialize portfolio shares and totals to zero for companies with charts.

    Args:
        companies (dict): Companies store.

    Returns:
        tuple[dict, dict]: Shares and totals dicts with zeros.
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
    """Delete selected companies, remove their data, and update portfolio stores.

    Args:
        clicks (list[int|None]): Clicks for each delete button.
        companies (dict): Companies store.
        children (list): Rendered list children.
        portfolio_shares (dict): Portfolio shares store.
        portfolio_totals (dict): Portfolio totals store.

    Returns:
        tuple: (children, companies, reset_clicks, portfolio_shares, portfolio_totals)
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
    """Rebuild activities options from current companies list.

    Args:
        companies (dict): Companies store including activity field.
        tabs (str): Current tab id (trigger only).

    Returns:
        list[dict]: Options for activities select component.
    """
    # get all the unique activities in companies dictionary
    activities = list(set([company["activity"] for company in companies.values()]))
    data = [{"label": activity, "value": activity} for activity in activities]
    return data
