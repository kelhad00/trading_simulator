import importlib

def download_market_data():
    """ Download market data from Yahoo Finance and save it into a data folder
        You can change the default path and data to download from the trade.defaults variables
    """
    try:
        importlib.import_module('.download_market_data', __package__)
    except ModuleNotFoundError:
        print('\nError while downloading market data.\nPlease make sure you have yahooquery installed and try again.')
        quit()

