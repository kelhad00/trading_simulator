import os
import pandas as pd

from trade.defaults import defaults as dlt

def get_news_dataframe():
    try:
        file_path = os.path.join(dlt.data_path, 'news.csv')
        news_df = pd.read_csv(file_path, sep=';')
        news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True, format='mixed')

        return news_df
    except:
        raise FileNotFoundError