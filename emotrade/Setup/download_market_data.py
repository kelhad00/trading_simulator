import os
import pandas as pd
from pandas.testing import assert_frame_equal
from yahooquery import Ticker

from emotrade.defaults import defaults as dlt

# Variables to set
# stock_list = [ # List of stocks to download
#     "MC.PA",  "OR.PA", "RMS.PA", "TTE.PA", "SAN.PA",
#     "AIR.PA", "SU.PA", "AI.PA",  "EL.PA",  "BNP.PA",
#     "KER.PA", "DG.PA",  "CS.PA", "SAF.PA", "RI.PA",
#     "DSY.PA", "STLAM.MI", "BN.PA",  "STMPA.PA",  "ACA.PA"
# ]
stock_list = list(dlt.companies.keys()) + list(dlt.indexes.keys())
periode_to_scrape = " 1mo"
each_time_interval = "5m"

print('For these stocks:', stock_list, '\n')

# Download market data
tickers = Ticker(
    stock_list,
    asynchronous = True,  # download with multiple threads
    formatted = True,     # all data will be returned as a dict
    # country = 'France',   # set country to France to get the right timezone
    progress=True         # show progress bar
)
print('Download Historical Prices...')
data = tickers.history(   # download data
    period   = periode_to_scrape,
    interval = each_time_interval,
    adj_timezone = False  # to standardize timezone
)

# Format data to be like yfinance output (previously used)
data = data.drop(['dividends'],axis=1).unstack(level=0).swaplevel(axis=1)
data.rename(
    columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"},
    inplace=True
)

# Add missing datetimes to fill gaps in the data
data = data.resample('5Min').asfreq()

# Convert timezone to Paris
data.index = pd.to_datetime(data.index, utc=True).tz_convert('Europe/Paris')

# Fill closed market data with the last available data.
data.fillna(method='ffill',inplace=True)
# Fill the nan data at the beginning of the dataframe with next available data
data.fillna(method='bfill',inplace=True)

# Add moving average using downloaded data
for stock in stock_list:
    data[stock,'long_MA'] = data[stock,'Close'].rolling(int(20)).mean()
    data[stock,'short_MA'] = data[stock,'Close'].rolling(int(50)).mean()

data = data.dropna()

# Show stucture of the downloaded data
print("Overview of the data:\n", data.head(), '\n')

# Create directory to save data
if not os.path.exists(dlt.data_path):
    print('Creating directory ' + dlt.data_path)
    os.mkdir(dlt.data_path)

# # Save data to multily CSV file
# for stock in stock_list:
#     file_path = os.path.join(dlt.data_path, 'market_data', stock + '.csv')
#     data[stock].to_csv(file_path)

# Save data to single CSV file
print('Saving data to ' + dlt.data_path + '/market_data.csv')
file_path = os.path.join(dlt.data_path, 'market_data.csv')
data.to_csv(file_path)

# Read data from CSV file and show its head to check if it is correct
imported_data = pd.read_csv(file_path, index_col=0, header=[0,1])
imported_data.index = pd.to_datetime(imported_data.index)

print('Download Historical Prices done\n\n Download Total Revenue...')

# Get company revenue
data = tickers.get_financial_data(['TotalRevenue','NetIncome'], trailing=False)
data = data.reset_index().set_index(['symbol','asOfDate']).T.drop('periodType')

print("Overview of the data:\n", data.head(), '\n')

# Save data to single CSV file
print('Saving data to '+ dlt.data_path + '/revenue.csv')
file_path = os.path.join(dlt.data_path, 'revenue.csv')
data.to_csv(file_path)

print('Download Total Revenue done')