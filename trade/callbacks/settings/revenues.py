from dash import callback, Output, Input, State, page_registry, html, dcc, no_update
import pandas as pd
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from trade.utils.graph.candlestick_charts import PLOTLY_CONFIG
from trade.utils.market import get_revenues_dataframe
from trade.utils.settings.create_market_data import get_generated_data
from yahooquery import Ticker
from trade.defaults import defaults as dlt
import os
import plotly.graph_objects as go

from trade.locales import translations as tls

@callback(
    Output("select-companies-revenues", "value", allow_duplicate=True),
    Input("select-all-companies-revenues", "n_clicks"),
    State("companies", "data"),
    prevent_initial_call=True
)
def select_all_companies(n, companies):
    if n is None:
        raise PreventUpdate
    value = [company for company in companies.keys() if companies[company]["got_charts"]]
    return value


@callback(
    Output("testo", "children"),
    Input("settings-tabs", "value"),
    Input("modal-revenues", "opened"),
    Input("select-companies-revenues", "value")
)
def display_revenues(tabs, modal, companies):
    if companies is None or companies == []:
        raise PreventUpdate

    revenues = get_revenues_dataframe()
    children = []
    for company in companies:
        try:

            # Format these data to be easily used
            df = revenues[company].T.reset_index()
            df['asOfDate'] = pd.to_datetime(df['asOfDate']).dt.year
            df['NetIncome'] = pd.to_numeric(df['NetIncome'], errors='coerce')
            df['TotalRevenue'] = pd.to_numeric(df['TotalRevenue'], errors='coerce')


            # Create the graph
            fig = go.Figure(data=[
                go.Bar(
                    name=tls[page_registry["lang"]]["revenue-graph"]['totalRevenue'],
                    x=df['asOfDate'], y=df['TotalRevenue']
                ),
                go.Bar(
                    name=tls[page_registry["lang"]]["revenue-graph"]['netIncome'],
                    x=df['asOfDate'], y=df['NetIncome']
                )
            ])
            fig.update_layout(
                title=f"Revenues for {company}",
            )
            children.append(
                dcc.Graph(
                    figure=fig,
                    config=PLOTLY_CONFIG,
                )
            )
        except Exception as e:
            print(e)
            children.append(dcc.Graph())

    return children


@callback(
    Output("modal-revenues", "opened"),
    Output("modal-select-companies-revenues", "value"),
    Input("button-modify-revenues", "n_clicks"),
    State("modal-revenues", "opened"),
    State("select-companies-revenues", "value"),
    prevent_initial_call=True
)
def open_modal(n, opened, companies):
    """
    Open the modal to generate charts and automatically select the company in the dropdown
    """
    return not opened, companies



@callback(
    Output("select-companies-revenues", "data"),
    Output("modal-select-companies-revenues", "data"),
    Input("settings-tabs", "value"),
    Input("companies", "data"),
)
def update_options_news_companies(tabs, companies):

    options = [{"label": company["label"], "value": stock} for stock, company in companies.items() if company["got_charts"]]
    return options, options



@callback(
    Output("modal-select-companies-revenues", "value", allow_duplicate=True),
    Input("modal-select-all-companies-revenues", "n_clicks"),
    State("companies", "data"),
    prevent_initial_call=True
)
def select_all_companies_modal(n, companies):
    if n is None:
        raise PreventUpdate
    value = [company for company in companies.keys() if companies[company]["got_charts"]]
    return value

@callback(
    Output("modal-input-container-revenues", "children"),
    Input("modal-select-companies-revenues", "value"),
    Input("modal-radio-mode-revenues", "value"),
)
def update_revenues_inputs(companies, mode):
    if companies is None or companies == [] or mode is None:
        return []

    df = get_generated_data()
    timestamps = pd.to_datetime(df.index)

    years = timestamps.year.unique()
    last_year = years[-1]

    children = []
    for company in companies:
        ticker = Ticker(company.upper())
        data = ticker.get_financial_data(["TotalRevenue", "NetIncome"])
        data['asOfDate'] = pd.to_datetime(data['asOfDate'])
        data = data.set_index('asOfDate')

        revenues_list = []
        net_incomes_list = []

        years = data.index.year.unique()
        years = years[years <= last_year]

        for year in years:
            yearly_data = data[:f"{year}-12-31"]
            revenue = yearly_data['TotalRevenue'].iloc[-1] if not yearly_data['TotalRevenue'].empty else None
            net_income = yearly_data['NetIncome'].iloc[-1] if not yearly_data['NetIncome'].empty else None
            revenues_list.append(revenue)
            net_incomes_list.append(net_income)

        children.append(
            html.Div(
                children=[
                    dmc.Text(company, weight=500),
                    *[html.Div([
                        dmc.NumberInput(
                            label=f"Select a revenue for {year}",
                            value=revenue,
                            disabled=True if mode == "auto" else False,
                            className="flex-1"
                        ),
                        dmc.NumberInput(
                            label=f"Select a net income for {year}",
                            value=income,
                            disabled=True if mode == "auto" else False,
                            className="flex-1"
                        )],
                        className="flex justify-between gap-4"
                    ) for year, revenue, income in zip(years, revenues_list, net_incomes_list)]
                ],
                className="flex flex-col gap-2"
            )
        )

    return children


@callback(
    Output("modal-revenues", "opened", allow_duplicate=True),
    Input("generate-revenues", "n_clicks"),
    State("modal-select-companies-revenues", "value"),
    State("modal-radio-mode-revenues", "value"),
    prevent_initial_call=True
)
def export_revenues(n, companies, mode):
    """
    Export the revenues
    Args:
        n: The number of clicks
        company: The company selected
        mode: The mode selected
    Returns:
        The revenues
    """
    if companies is None or companies == [] or mode is None:
        raise PreventUpdate

    df = get_generated_data()
    timestamps = pd.to_datetime(df.index)

    years = timestamps.year.unique()
    last_year = years[-1]

    existing_revenues = get_revenues_dataframe()

    try:
        symbols_list = existing_revenues.columns.get_level_values('symbol').unique()
    except:
        symbols_list = []



    for company in companies:
        ticker = Ticker(company.upper())
        # Get company revenue
        data = ticker.get_financial_data(['TotalRevenue', 'NetIncome'], trailing=False)
        data = data.reset_index().set_index(['symbol', 'asOfDate']).T.drop('periodType')

        # get data before the last year
        data = data.loc[:, data.columns.get_level_values('asOfDate').year <= last_year]

        if company in symbols_list:
            existing_revenues.drop(columns=company, level=0, inplace=True)

        # Concatenate the new data with the existing data
        existing_revenues = pd.concat([existing_revenues, data], axis=1)

    # Save data to single CSV file
    file_path = os.path.join(dlt.data_path, 'revenue.csv')
    existing_revenues.to_csv(file_path)

    return False



@callback(
    Output("testo", "children", allow_duplicate=True),
    Input("button-delete-revenues", "n_clicks"),
    State("select-companies-revenues", "value"),
    prevent_initial_call=True
)
def delete_revenues(n, companies):
    """
    Delete the revenues
    Args:
        n: The number of clicks
        company: The company selected
    Returns:
        The revenues
    """
    if companies is None or companies == []:
        raise PreventUpdate

    revenues = get_revenues_dataframe()
    for company in companies:
        revenues.drop(columns=company, level=0, inplace=True)

    # Save data to single CSV file
    file_path = os.path.join(dlt.data_path, 'revenue.csv')
    revenues.to_csv(file_path)

    return dcc.Graph()