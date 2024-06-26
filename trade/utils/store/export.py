import pandas as pd
from datetime import datetime
import os
from dash import page_registry

from trade.defaults import defaults as dlt
from trade.Locales import translations as tls


def format_portfolio_dataframe(df, name):
    df = pd.DataFrame.from_dict(df, orient='index').T
    columns = dict(zip(df.columns, [col + name for col in df.columns]))
    df.rename(columns=columns, inplace=True)
    return df

def format_requests_dataframe(request_list):
    new_columns_data = {}
    df = pd.DataFrame(request_list, columns=['action', 'shares', 'company', 'price']).T
    for i in range(1, len(request_list)):  # Parcourir les 10 actions (de 1 à 10)
        action_data = df[i]  # Extraire les données pour l'action i
        action_col_name = f"action-{i}"
        price_col_name = f"price-{i}"
        share_col_name = f"shares-{i}"

        new_columns_data[action_col_name] = action_data['action']
        new_columns_data[price_col_name] = action_data['price']
        new_columns_data[share_col_name] = action_data['shares']

    return pd.DataFrame.from_dict(new_columns_data, orient="index").T



def format_charts_type(chart_type):
    lang = page_registry['lang']
    if chart_type == tls[lang]['tab-market']:
        return "market"
    else:
        return "revenue"



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
        trigger=None
):
    """ Periodically save state of the trade into csv
    """

    charts = format_charts_type(graph_type)
    requests = format_requests_dataframe(request_list)
    shares = format_portfolio_dataframe(shares, "-shares")
    totals = format_portfolio_dataframe(totals, "-totals")

    df = pd.DataFrame({
        "host-timestamp": [datetime.now().timestamp()],
        "market-timestamp": [timestamp],
        "selected-company": [company_id],
        "cashflow": [cashflow],
        "form-action": [form_type],
        "chart-type": [charts],
        "is_news_description_displayed" : [False if news_title is None else True],
        "news_title" : [news_title]
    })

    df = df.merge(shares, how='left', left_index=True, right_index=True)
    df = df.merge(totals, how='left', left_index=True, right_index=True)
    df = df.merge(requests, how='left', left_index=True, right_index=True)



    # Save the header only once and append the rest
    file_path = os.path.join(dlt.data_path, 'interface-logs.csv')
    # print(df)
    if os.path.isfile(file_path):
        df.to_csv(file_path, mode='a', index=False, header=False)
    else:
        df.to_csv(file_path, index=False)

