import os
import pandas as pd

from trade.defaults import defaults as dlt

# def get_market_dataframe():
#     try:
#         # file_path = os.path.join(dlt.data_path, 'generated_data.csv')
#         file_path = os.path.join(dlt.data_path, 'market_data.csv')
#         df = pd.read_csv(file_path, index_col=0, header=[0, 1])
#
#         return df
#     except:
#         print('ERROR: No market data found in ' + dlt.data_path + ' folder.')
#         raise FileNotFoundError

def get_market_dataframe(generated=True):
    file = 'generated_data.csv' if generated else 'market_data.csv'

    try:
        file_path = os.path.join(dlt.data_path, file)
        df = pd.read_csv(file_path, index_col=0, header=[0, 1])
        return df
    except:
        print('ERROR: No market data found in ' + dlt.data_path + ' folder.')
        raise FileNotFoundError



def get_price_dataframe():
    df = get_market_dataframe()
    price_list = df.xs('Close', axis=1, level=1)
    return price_list


def get_first_timestamp(market_df, news_df, range=0):
    # try:
    #     # set the timestamp to the older shared date between news and market data
    #     # if news_df is the newer one, set the timestamp to the first date share with news_df
    #     if news_df.min().date.strftime('%Y-%m-%d') > market_df.index.min()[:10]:
    #         timestamp = market_df.loc[market_df.index >= news_df.min().date.strftime('%Y-%m-%d')].index[0]
    #     else:
    #         timestamp = market_df.index.min()
    # except:
    #     timestamp = market_df.index.min()

    try:
        timestamp = market_df.index[range]
        return timestamp
    except:
        return 0
