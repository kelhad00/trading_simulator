from datetime import datetime
from emotrade.Scraping.scrapping import random_news_scraping


def scraping_news(starting_date = '30/04/2023'):
    """ Scrap news from ZoneBourse and save it in a Data folder
    """
    random_news_scraping(starting_date)
    return 0

