import importlib

"""
Provides scripts files as functions
"""

def download_market_data():
    """ Download market data from Yahoo Finance and save it a Data folder
    """
    importlib.import_module('.download_market_data', __package__)

# Provide scrapping_news function into Setup module
# without having to import it from Scraping module
from .scraping_news import scraping_news