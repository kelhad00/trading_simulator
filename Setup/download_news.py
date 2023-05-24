"""
This script is used to download news from the internet and save them in a csv file.
This is a temporary solution until we find a way to get real news from the internet.
"""
import os
import pandas as pd
from pandas.testing import assert_frame_equal

#TODO: remove this after adding real news
NEWS_DATA = pd.DataFrame({
	"Date": ["05/05/2023 10:03", "05/05/2023 11:27","05/05/2023 11:45","05/05/2023 11:45","05/05/2023 11:45"],
	"Title": ['Tesla bought Twitter','CAC40 is falling','News','News 23', 'News NEWS']
})

print(NEWS_DATA.head())

# Create directory to save data
if not os.path.exists("Data"):
    os.mkdir("Data")

file_path = os.path.join('Data', 'news.csv')
NEWS_DATA.to_csv(file_path, index=False, sep=';')

# Read data from CSV file and show its head to check if it is correct
df = pd.read_csv(file_path, sep=';')
print("Checking if the data as been saved correctly:")

assert_frame_equal(NEWS_DATA, df, check_dtype=False)

print('Download done')