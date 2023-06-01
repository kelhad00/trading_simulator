from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re

from trading_simulator.Scraping.convert_date import convert_date

def titles_scraping(title_url):
    title_request = requests.get('https://www.zonebourse.com' + title_url)
    title_soup = BeautifulSoup(title_request.content, 'html.parser')
    try:
        title = title_soup.find('h1', attrs={'itemprop': 'headline name'}).text
    except AttributeError:
        try:
            title = title_soup.find('h1', attrs={'class': 'title title__primary mb-15 txt-bold'}).text
        except AttributeError:
            try:
                title = title_soup.find('h1', attrs={'class': 'title title__primary txt-bold'}).text
            except AttributeError:
                title = 'ERROR'
                print("Error_title")
    return title


def articles_scraping(article_url):
    article_request = requests.get('https://www.zonebourse.com' + article_url)
    article_soup = BeautifulSoup(article_request.content, 'html.parser')
    article_content = 'Null'
    try:
        article_content = article_soup.find('div', attrs={'id': 'grantexto'}).text
    except AttributeError:
        try:
            article_content = article_soup.find('article', attrs={'class': 'p-10 p-m-15'}).text
        except AttributeError:
            try:
                article_content = article_soup.find('article', attrs={
                    'data-io-article-url': 'https://www.zonebourse.com/' + article_url}).text
            except AttributeError:
                print('Error_content')
    return article_content

def date_scraping(date_url):
    full_url = "https://www.zonebourse.com" + date_url
    date_request = requests.get(full_url)
    date_soup = BeautifulSoup(date_request.content, 'html.parser')
    try:
        date = date_soup.find('meta', attrs={'itemprop': 'datePublished'}).previous.text.replace(' | ', ' ')
        date = re.sub('[a-zA-Z]', '', date).strip()
    except AttributeError:
        try:
            date = convert_date(date_soup.find('div', attrs={'class': 'c-6 mb-15'}).text)
        except AttributeError:
            try:
                date = convert_date(date_soup.find('p', attrs={'class': 'txt-muted mt-10 mb-0 mb-15 pb-15'}).text)
            except AttributeError:
                date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return date