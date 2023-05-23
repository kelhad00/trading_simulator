import yfinance as yf
import os
import pandas as pd
from pandas.testing import assert_frame_equal

# Variables to set
stock_list = [ # List of stocks to download
    "MC.PA",  "TTE.PA", "SAN.PA", "OR.PA",  "SU.PA", \
    "AI.PA",  "AIR.PA", "BNP.PA", "DG.PA",  "CS.PA", \
    "RMS.PA", "EL.PA",  "SAF.PA", "KER.PA", "RI.PA", \
    "STLAM.MI",  "BN.PA",  "STMPA.PA",  "CAP.PA", "SGO.PA"
]
periode_to_scrape = " 1mo"
each_time_interval = "15m"

print('For these stocks:', stock_list, '\n')

# Download market data
data = yf.download(
    tickers  = stock_list,
    period   = periode_to_scrape,
    interval = each_time_interval,
    group_by = "ticker", # group columns by stock
    auto_adjust = True,
    prepost  = True,
    threads  = True,     # download with multiple threads
    proxy    = None
)

# Show stucture of the downloaded data
print('data fields downloaded:', set(data.columns.get_level_values(0)))
print("Overview of the data:\n", data.head(), '\n')

# Create directory to save data
if not os.path.exists("Data"):
    print('Creating directory Data')
    os.mkdir("Data")

# # Save data to multily CSV file
# for stock in stock_list:
#     file_path = os.path.join('market_data', stock + '.csv')
#     data[stock].to_csv(file_path)

# Save data to single CSV file
print('Saving data to Data/market_data.csv')
file_path = os.path.join('Data', 'market_data.csv')
data.to_csv(file_path)

# Read data from CSV file and show its head to check if it is correct
imported_data = pd.read_csv(file_path, index_col=0, header=[0,1])
imported_data.index = pd.to_datetime(imported_data.index)
print("Checking if the data as been saved correctly:")

assert_frame_equal(data, imported_data, check_dtype=False)

print('Download done')