from dash import Output, Input, State, callback, html, page_registry

from trade.utils.create_table import create_table
from trade.utils.market import get_market_dataframe, get_first_timestamp, get_price_dataframe
from trade.utils.news import get_news_dataframe

from trade.Locales import translations as tls

import dash_mantine_components as dmc

import numpy as np
import pandas as pd

#
# @callback(
#     Output('portfolio-totals', 'data'),
#     Input('periodic-updater', 'n_intervals'),
#     State('portfolio-shares', 'data'),
#     State('portfolio-totals', 'data'),
#     State('timestamp', 'data'),
#     prevent_initial_call=True
# )
# def update_porfolio_totals(n, shares, totals, timestamp):
#     """ Update the portfolio total price with the latest market data price"""
#     price_df = get_price_dataframe()
#     shares = pd.DataFrame.from_dict(shares, orient='index', columns=['Shares'])
#     totals = pd.DataFrame.from_dict(totals, orient='index', columns=['Totals'])
#
#     if not timestamp == "":
#         # Update the total price of each stock
#         totals['Totals'] = shares['Shares'] * price_df.loc[timestamp, totals.index]
#
#     return totals['Totals'].to_dict()



@callback(
    Output('portfolio-cashflow', 'children'),
    Output('portfolio-investment', 'children'),
    Input('periodic-updater', 'n_intervals'),
    Input('portfolio-totals', 'data'),
    Input('cashflow', 'data'),
)
def update_portfolio(n, totals, cashflow):
    """ Update the portfolio total price"""
    totals = pd.Series(totals)
    return f"{round(cashflow, 2)}€", f"{round(cashflow + totals.sum(), 2)}€",


@callback(
    Output("portfolio-table-container", "children"),
    Input('periodic-updater', 'n_intervals'),
    Input('portfolio-totals', 'data'),
    Input('portfolio-shares', 'data'),
)
def update_portfolio(n, totals, shares):
    totals = pd.Series(totals)
    shares = pd.Series(shares)

    lang = page_registry['lang']

    df = pd.concat([shares, totals], axis=1)
    df.columns = [tls[lang]['portfolio-columns']['Shares'], tls[lang]['portfolio-columns']['Total']]
    df.reset_index(inplace=True)
    df.rename(columns={'index': tls[lang]['portfolio-columns']['Stock']}, inplace=True)


    #round column totals to 2 decimal places
    df[tls[lang]['portfolio-columns']['Total']] = df[tls[lang]['portfolio-columns']['Total']].round(2)

    return dmc.Table(
        children=create_table(df),
    )


@callback(
    Output("timer", "children"),
    Input("periodic-updater", "n_intervals"),
    State("timestamp", "data"),
)
def cb_update_timestamp(n, timestamp):
    market_df = get_market_dataframe()
    news_df = get_news_dataframe()

    if timestamp == "":
        print("hello")
        timestamp = get_first_timestamp(market_df, news_df)
    else:
        i = np.minimum(market_df.index.get_loc(timestamp) + 1, len(market_df.index) - 1)
        timestamp = market_df.index[i]

    # only return the date for display (ex : 9 04 2021) in french format
    timestamp = pd.to_datetime(timestamp)
    return timestamp.strftime("%Y-%m-%d")


