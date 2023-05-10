import yfinance as yf
import os

# Variables to set
stock_list = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "NVDA", "PEP", "COST"] # List of NASDAQ to scrape
periode_to_scrape = "1y"
each_time_interval = "1h"


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
    file_path = os.path.join('market_data', stock + '.csv')
    data[stock].to_csv(file_path)
