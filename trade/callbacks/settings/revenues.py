from dash import callback, Output, Input, State, page_registry, html
import pandas as pd
import dash_mantine_components as dmc

from trade.utils.settings.create_market_data import get_generated_data
from yahooquery import Ticker



@callback(
    Output("revenues-select-company", "data"),
    Input("settings-tabs", "value"),
    Input("companies", "data"),
)
def update_options_news_companies(tabs, companies):

    options = [{"label": company["label"], "value": stock} for stock, company in companies.items() if company["got_charts"]]
    return options


@callback(
    Output("revenues-inputs-container", "children"),
    Input("revenues-select-company", "value"),
    Input("input-revenue-mode", "value"),
)
def update_revenues_inputs(company, mode):
    """
    Update the revenues inputs
    Args:
        company: The company selected
        mode: The mode selected
    Returns:
        The revenues inputs
    """
    if company is None or mode is None:
        return []

    df = get_generated_data()[company]
    timestamps = pd.to_datetime(df.index)
    years = timestamps.year.unique()
    years = [2020, 2021, 2022]

    if mode == "manual":
        return [html.Div(
            dmc.NumberInput(label=f"Select a revenue for {year}", min=0),
            className="flex flex-col gap-2"
        ) for year in years]

    if mode == "auto":
        ticker = Ticker(company.upper())
        data = ticker.get_financial_data("TotalRevenue")
        data = data.reset_index()

        revenues = [
            data[data['asOfDate'] == f"{year}-12-31"]['TotalRevenue'].iloc[0]
            for year in years]

        return [html.Div(
            dmc.NumberInput(
                label=f"Select a revenue for {year}",
                value=revenue,
                disabled=True
            ),
            className="flex flex-col gap-2"
        ) for year, revenue in zip(years, revenues)]


