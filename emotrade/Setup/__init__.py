import importlib

"""
Provides scripts files as functions
"""

def download_market_data():
    """ Download market data from Yahoo Finance and save it a Data folder
    """
    importlib.import_module('.download_market_data', __package__)