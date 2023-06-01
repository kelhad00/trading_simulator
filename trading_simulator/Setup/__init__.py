import importlib

"""
Provides scripts files as functions
"""

def download_market_data():
    """ Download market data from Yahoo Finance and save it a Data folder
    """
    importlib.import_module('.download_market_data', __package__)

def scraping_news():
    """ Scrap news from ZoneBourse and save it a Data folder
    """
    importlib.import_module('.scraping_with_bs4', __package__)