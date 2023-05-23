"""
This script is used to download news from the internet and save them in a csv file.
This is a temporary solution until we find a way to get real news from the internet.
"""

import pandas as pd

#TODO: remove this after adding real news
NEWS_DATA = pd.DataFrame({
	"Date": ["05/05/2023 10:03", "05/05/2023 11:27","05/05/2023 11:45","05/05/2023 11:45","05/05/2023 11:45"],
	"Title": ['Tesla bought Twitter','CAC40 is falling','News','News 23', 'News NEWS']
})

print(NEWS_DATA.head())

NEWS_DATA.to_csv('news.csv', index=False, sep=';')