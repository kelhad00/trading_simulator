import importlib

"""
Provides scripts files as functions
"""

def download_market_data():
    """ Download market data from Yahoo Finance and save it into a data folder
        You can change the default path and data to download from the app.defaults variables
    """
    importlib.import_module('.download_market_data', __package__)