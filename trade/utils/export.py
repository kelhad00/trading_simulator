from uuid import uuid4

import pandas as pd
from datetime import datetime
import os
from dash import page_registry

from trade.defaults import defaults as dlt
from trade.locales import translations as tls


def format_portfolio_dataframe(df, name):
    df = pd.DataFrame.from_dict(df, orient='index').T
    columns = dict(zip(df.columns, [col + name for col in df.columns]))
    df.rename(columns=columns, inplace=True)
    return df

def format_requests_dataframe(request_list):
    new_columns_data = {}
    df = pd.DataFrame(request_list, columns=['action', 'shares', 'company', 'price']).T
    for i in range(0, 10):  # Parcourir les 10 actions (de 1 à 10)
        action_col_name = f"request-{i+1}"
        try:
            action_data = df[i]  # Extraire les données pour l'action i
            new_columns_data[action_col_name] = f"{action_data['action']} {action_data['price']} {action_data['shares']} {action_data['company']}"
        except:
            new_columns_data[action_col_name] = None

    return pd.DataFrame.from_dict(new_columns_data, orient="index").T



def format_charts_type(chart_type):
    lang = page_registry['lang']
    if chart_type == tls[lang]['tab-market']:
        return "market"
    else:
        return "revenue"


def format_deleted_requests(deleted_request):
    if deleted_request is None:
        deleted_request = []
    else:
        deleted_request = list(deleted_request)
    return deleted_request


def export_data(
        timestamp,
        request_list,
        cashflow,
        shares,
        totals,
        company_id,
        news_title,
        graph_type,  # used to know which type of charts is displayed
        form_type,  # used to know if user is going to buy or sell
        deleted_request=None,
        trigger=None
):
    """ Periodically save state of the trade into csv
    """

    deleted_request = format_deleted_requests(deleted_request)
    charts = format_charts_type(graph_type)
    requests = format_requests_dataframe(request_list)
    shares = format_portfolio_dataframe(shares, "-shares")
    totals = format_portfolio_dataframe(totals, "-totals")

    # generate an uuid
    uuid = str(uuid4())

    df = pd.DataFrame({
        "uuid": [uuid],
        "market-timestamp": [timestamp],
        "host-timestamp": [datetime.now().timestamp()],
        "cashflow": [cashflow],
        "selected-company": [company_id],
        "form-action": [form_type],
        "chart-type": [charts],
        "is_news_description_displayed" : [False if news_title is None else True],
        "news_title" : [news_title],
    })

    portfolio_df = pd.DataFrame({"uuid": [uuid]})
    portfolio_df = portfolio_df.merge(shares, how='left', left_index=True, right_index=True)
    portfolio_df = portfolio_df.merge(totals, how='left', left_index=True, right_index=True)

    request_df = pd.DataFrame({"uuid": [uuid], "deleted-request": [deleted_request]})
    request_df = request_df.merge(requests, how='left', left_index=True, right_index=True)

    # Save the header only once and append the rest
    file_path = os.path.join(dlt.data_path, 'export', 'interface-logs.csv')
    portfolio_path = os.path.join(dlt.data_path, 'export', 'portfolio-logs.csv')
    request_path = os.path.join(dlt.data_path, 'export', 'request-logs.csv')

    save_df(df, file_path)
    save_df(portfolio_df, portfolio_path)
    save_df(request_df, request_path)


def save_df(df, file_path):
    if os.path.isfile(file_path):
        df.to_csv(file_path, mode='a', index=False, header=False)
    else:
        df.to_csv(file_path, index=False)
