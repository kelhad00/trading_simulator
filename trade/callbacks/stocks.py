import os.path
import pandas as pd

from dash import callback, Input, Output, State, ALL, no_update, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from trade.utils.settings.create_market_data import bull_trend, bear_trend, flat_trend, export_generated_data, \
    get_generated_data, delete_generated_data
from trade.utils.settings.display import display_chart
from trade.utils.settings.data_handler import scale_market_data, load_data, get_data_size
from trade.layouts.settings.charts import timeline_item, ordinal
from trade.defaults import defaults as dlt

@callback(
    Output("companies", "data"),
    Output("notifications", "children"),
    Input("add-company", "n_clicks"),
    State("input-stock", "value"),
    State("input-company", "value"),
    State("companies", "data"),
)
def update_companies(n, stock, company, companies):
    notif = no_update
    if n:
        companies[stock] = company
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
)
def display_companies(companies):
    return [
        dmc.Paper([
            html.Div([
                dmc.Text("Stock", weight=500),
                dmc.Text(stock, size="sm"),
            ], className="flex flex-col flex-1"),
            html.Div([
                dmc.Text("Company", weight=500),
                dmc.Text(company, size="sm"),
            ], className="flex flex-col flex-[2]"),
            dmc.ActionIcon(
                DashIconify(icon="material-symbols:delete-outline", width=20),
                size="lg",
                radius="md",
                color="dark",
                variant="outline",
                id={"type": "delete-stock", "index": stock},
                n_clicks=0,
            ),
        ],
            className="flex justify-between gap-4 items-center",
            radius="md",
            p="xs",
            withBorder=True,
        ) for stock, company in companies.items()
    ]


@callback(
    Output("select-company", "data"),
    Output("select-company-modal", "data"),
    Output("select-company", "value"),
    Input("companies", "data"),
    State("select-company", "value"),
)
def update_select_company_options(companies, company):
    options = {**companies, **dlt.indexes}
    if company not in options.keys():
        company = list(options.keys())[0]

    options = [{"label": v, "value": k} for k, v in options.items()]

    return options, options, company

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
    children = [child for index, child in enumerate(children) if not clicks[index]]

    if 1 in clicks:
        index = clicks.index(1)
        stock = list(companies.keys())[index]
        del companies[stock]
        delete_generated_data(stock)

    return children, companies, [0] * len(clicks)
