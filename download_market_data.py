import yfinance as yf
import os

# Variables to set
stock_list = [ # List of stocks to download
    "MC.PA",  "TTE.PA", "SAN.PA", "OR.PA",  "SU.PA", \
    "AI.PA",  "AIR.PA", "BNP.PA", "DG.PA",  "CS.PA", \
    "RMS.PA", "EL.PA",  "SAF.PA", "KER.PA", "RI.PA", \
    "STLAM.MI",  "BN.PA",  "STMPA.PA",  "CAP.PA", "SGO.PA"
]
periode_to_scrape = " 1mo"
each_time_interval = "15m"

print('stock_list:', stock_list)

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
print(data.head())

# Create directory to save data
if not os.path.exists("market_data"):
    os.mkdir("market_data")

# Save data to CSV file
for stock in stock_list:
    data[stock].to_csv('market_data/'+ stock +'.csv')
