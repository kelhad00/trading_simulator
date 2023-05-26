import importlib

"""
Provides scripts files as functions
"""

def download_market_data():
    importlib.import_module('.download_market_data', __package__)

def scraping_news():
    importlib.import_module('.scraping_with_bs4', __package__)