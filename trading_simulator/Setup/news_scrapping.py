from stocknews import StockNews
import pandas as pd
import numpy as np
import datetime

# GET THE DATA
COMP = [ # List of stocks to download
    "MC.PA",  "TTE.PA", "SAN.PA", "OR.PA",  "SU.PA", \
    "AI.PA",  "AIR.PA", "BNP.PA", "DG.PA",  "CS.PA", \
    "RMS.PA", "EL.PA",  "SAF.PA", "KER.PA", "RI.PA", \
    "STLAM.MI",  "BN.PA",  "STMPA.PA",  "CAP.PA", "SGO.PA"
]
# sn = StockNews(COMP, wt_key='MY_WORLD_TRADING_DATA_KEY') 
# df = sn.summarize()

# READ THE DATA
dff = pd.read_csv('data/news.csv',sep=';',usecols=['stock','title','summary','p_date']) # 'sentiment_title'


def title_wanted():
    list_tile = list(dff['title'])
    
    # print(list_title)
    for T in list_title:
        if 'The title' in T: 
            print(dff[dff['summary'][dff['title']==T]]) #n possible ?
            #Add to the text descrption
            text_desc = str(dff[dff['summary'][dff['title']==T]])

    return text_desc

date_wanted()

# my_df = dff[dff['p_date']=='CAP.PA_2023-05-02']
# required_df =df.loc[df['hits']>20]
# print(my_df)


# get current date
# current_date = datetime.date.today()
# date = datetime.date(2023, 5, 19)
# print(date)