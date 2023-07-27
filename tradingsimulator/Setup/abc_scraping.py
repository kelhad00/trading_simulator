from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
from datetime import datetime

cac40data = [['LVMH MOËT HENNESSY LOUIS VUITTON SE', 'MC'],
             ["L'ORÉAL", 'OR'],
             ['HERMÈS INTERNATIONAL', 'RMS'],
             ['TOTALENERGIES SE', 'TTE'],
             ['SANOFI', 'SAN'],
             ['AIRBUS SE', 'AIR'],
             ['SCHNEIDER ELECTRIC SE', 'SU'],
             ['AIR LIQUIDE', 'AI'],
             ['ESSILORLUXOTTICA', 'EL'],
             ['BNP PARIBAS', 'BNP'],
             ['KERING', 'KER'],
             ['VINCI', 'DG'],
             ['AXA', 'CS'],
             ['SAFRAN', 'SAF'],
             ['PERNOD RICARD', 'RI'],
             ['DASSAULT SYSTÈMES SE', 'DSY'],
             ['STELLANTIS N.V.', 'STLAP'],
             ['DANONE', 'BN'],
             ['STMICROELECTRONICS N.V.', 'STMPA'],
             ['CRÉDIT AGRICOLE S.A.', 'ACA']]
company_df = pd.DataFrame(cac40data, columns=['name', 'ticker'])

# #create the csv file with the headers
# with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
#     writer = csv.writer(csvfile, delimiter=';')
#     writer.writerow(['title', 'content', 'ticker', 'date'])

def save_news_in_file(news, filename):
    with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow([news['title'], news['content'], news['ticker'], news['date']])
        # writer.writerow([news['title'], news['ticker'], news['date']])
    return 0


def article_scraping(article_url):
    article_request = requests.get('https://www.abcbourse.com' + article_url)
    article_soup = BeautifulSoup(article_request.content, 'html.parser')

    try:
        title = article_soup.find('h1', attrs={'class': 'h1b'}).text
        title = title.strip()

    except AttributeError:
        print('Error_title')
        title = 'ERROR'

    try:
        content = article_soup.find('div', attrs={'class': 'txtbig content_news'}).text
        content = content.replace('(CercleFinance.com) - ', '').strip()
        content = content.replace("Vous avez aimé cet article ? Partagez-le avec vos amis avec les boutons ci-dessous.", '').strip()


    except AttributeError:
        print('Error_content')
        content = 'ERROR'

    article = {'title': title, 'content': content}
    return article


def compare_date(date):
    date_str = date.split("/")
    date_int = date_str[2] + date_str[1] + date_str[0]
    return int(date_int)


def company_news_scraping(company_ticker, date_until_scrap):
    current_date = datetime.now().strftime("%d/%m/%y")
    page_index = 1
    print('**********Scraping of ' + company_df[company_df['ticker'] == company_ticker]['name'].values[0] + ' news**********')
    while compare_date(date_until_scrap) < compare_date(current_date):
        url = 'https://www.abcbourse.com/marches/news_valeur/' + company_ticker + 'p/' + str(page_index)
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')
        table = soup.find('div', attrs={'class': 'newslft'})
        for row in table.findAll('div'):
            quote = {}
            quote['title'] = article_scraping(row.a['href'])['title']
            quote['content'] = article_scraping(row.a['href'])['content']
            quote['ticker'] = company_ticker
            quote['date'] = row.span.text
            print(quote['date'])
            current_date = str(quote['date']).split(' ')[0]
            if compare_date(date_until_scrap) > compare_date(current_date):
                break
            save_news_in_file(quote, '20_month_scraping_v2.csv')
        page_index += 1
    return 1


for company in cac40data:
    company_news_scraping(company[1], '01/11/21')

# company_news_scraping('STLAP', '01/01/22')