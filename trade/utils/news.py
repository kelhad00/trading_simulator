import os
import pandas as pd

from trade.defaults import defaults as dlt

def get_news_dataframe():
    try:
        file_path = os.path.join(dlt.data_path, 'news.csv')
        news_df = pd.read_csv(file_path, sep=';')
        # Strip timezone suffix (+02:00 / +01:00) so both date formats parse cleanly
        news_df['date'] = news_df['date'].astype(str).str.replace(
            r'\s*[+-]\d{2}:\d{2}$', '', regex=True
        )
        news_df['date'] = pd.to_datetime(news_df['date'], dayfirst=True, format='mixed')
        return news_df
    except Exception as e:
        print(f'[NEWS] get_news_dataframe error: {e}')
        raise FileNotFoundError