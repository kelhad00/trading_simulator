from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import csv

cac40data = [['LVMH MOËT HENNESSY LOUIS VUITTON SE', 'MC', 'LVMH-MOET-HENNESSY-LOUIS-4669'],
             ["L'ORÉAL", 'OR', 'L-OREAL-4666'],
             ['HERMÈS INTERNATIONAL', 'RMS', 'HERMES-INTERNATIONAL-4657'],
             ['TOTALENERGIES SE', 'TTE', 'TOTALENERGIES-SE-4717'],
             ['SANOFI', 'SAN', 'SANOFI-4698'],
             ['AIRBUS SE', 'AIR', 'AIRBUS-SE-4637'],
             ['SCHNEIDER ELECTRIC SE', 'SU', 'SCHNEIDER-ELECTRIC-SE-4699'],
             ['AIR LIQUIDE', 'AI', 'AIR-LIQUIDE-4605'],
             ['ESSILORLUXOTTICA', 'EL', 'ESSILORLUXOTTICA-4641'],
             ['BNP PARIBAS', 'BNP', 'BNP-PARIBAS-4618'],
             ['KERING', 'KER', 'KERING-4683'],
             ['VINCI', 'DG', 'VINCI-4725'],
             ['AXA', 'CS', 'AXA-4615'],
             ['SAFRAN', 'SAF', 'SAFRAN-4696'],
             ['PERNOD RICARD', 'RI', 'PERNOD-RICARD-4681'],
             ['DASSAULT SYSTÈMES SE', 'DSY', 'DASSAULT-SYSTEMES-SE-4635'],
             ['STELLANTIS N.V.', 'STLAM', 'STELLANTIS-N-V-117814143'],
             ['DANONE', 'BN', 'DANONE-4634'],
             ['STMICROELECTRONICS N.V.', 'STMPA', 'STMICROELECTRONICS-N-V-4710'],
             ['CRÉDIT AGRICOLE S.A.', 'ACA', 'CREDIT-AGRICOLE-S-A-4735']]
company_df = pd.DataFrame(cac40data, columns=['name', 'ticker', 'url'])
quotes = []

# def save_dataset_in_file(datas):
#     filename = 'news.csv'
#     df = pd.DataFrame(datas)
#     # append the new data to the old file with the old data and delete the header and delete the duplicates
#     df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';', mode='a')
#     df = pd.read_csv(filename, sep=';')
#     # delete the second header only
#     df = df[df['title'] != 'title']
#     # delete the duplicates
#     df = df.drop_duplicates()
#     # save the new data
#     df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
#     return print('File saved')

def save_news_in_file(news, filename):
    with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow([news['title'], news['content'], news['ticker'], news['date']])
    return print('File saved')

def titles_scraping(title_url):
    title_request = requests.get('https://www.zonebourse.com' + title_url)
    title_soup = BeautifulSoup(title_request.content, 'html.parser')
    try:
        title = title_soup.find('h1', attrs={'itemprop': 'headline name'}).text
    except AttributeError:
        try:
            title = title_soup.find('h1', attrs={'class': 'title title__primary mb-15 txt-bold'}).text
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
    except AttributeError:
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return date


def random_news_scraping():
    random_url = "https://www.zonebourse.com/actualite-bourse/societes/"
    random_request = requests.get(random_url)
    random_soup = BeautifulSoup(random_request.content, 'html.parser')
    random_table = random_soup.find('table', attrs={'id': 'newsScreener'})
    for row in random_table.findAll('tr', attrs={'class': '""'}):
        try:
            quote = {}
            quote['title'] = row.a.text.replace('\n', '').strip()
            quote['content'] = articles_scraping(row.a['href'])
            quote['ticker'] = row.span.text.replace('\n', '').strip()
            quote['date'] = row.time['title']
            quotes.append(quote)
            print(quote)
            # save_news_in_file(quote, 'news.csv')
        except TypeError:
            continue
    return quotes

def company_news_scraping(company_ticker):
    company_url = company_df[company_df['ticker'] == company_ticker]['url'].values[0]
    for i in range(1, 31):
        print('Page ' + str(i))
        url = 'https://www.zonebourse.com/cours/action/' + company_url + '/actualite-historique/&nbstrat=0&&fpage=' + str(i)
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')
        table = soup.find('table', attrs={'id': 'ALNI4'})
        for row in table.findAll('tr'):
            try:
                quote = {}
                quote['title'] = titles_scraping(row.a['href'])
                # quote['content'] = articles_scraping(row.a['href']).replace('\n\n', '\n')
                quote['content'] = 'wait'
                quote['ticker'] = company_ticker
                quote['date'] = date_scraping(row.a['href'])
                quotes.append(quote)
                save_news_in_file(quote, 'news.csv')
            except TypeError:
                continue
    return quotes

company_news_scraping("MC")