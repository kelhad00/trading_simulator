from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import os

cac40data = [['LVMH MOËT HENNESSY LOUIS VUITTON SE','MC', 'LVMH-MOET-HENNESSY-LOUIS-4669'],
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

def save_news_in_file(datas):
    filename = os.path.join('Data', 'news_by_bs4.csv')
    df = pd.DataFrame(datas)
    # append the new data to the old file with the old data and delete the header and delete the duplicates
    df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';', mode='a')
    df = pd.read_csv(filename, sep=';')
    # delete the second header only
    df = df[df['article'] != 'article']
    # delete the duplicates
    df = df.drop_duplicates()
    # save the new data
    df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
    return print('File saved')

def random_news_scraping():
    random_url = "https://www.zonebourse.com/actualite-bourse/societes/"
    random_request = requests.get(random_url)
    random_soup = BeautifulSoup(random_request.content, 'html.parser')
    random_table = random_soup.find('table', attrs={'id': 'newsScreener'})
    for row in random_table.findAll('tr', attrs={'class': '""'}):
        try:
            quote = {}
            quote['article'] = row.a.text.replace('\n', '').strip()
            quote['ticker'] = row.span.text.replace('\n', '').strip()
            quote['date'] = row.time['title']
            quotes.append(quote)
        except TypeError:
            continue
    return quotes

def convert_date(website_date):
    try:
        datetime.strptime(website_date, '%H:%M')
        website_date = datetime.now().strftime('%d/%m/%Y')
    except ValueError:
        website_date = website_date.replace('janvier', 'January').replace('février', 'February').replace('mars', 'March').replace('avril', 'April').replace('mai', 'May').replace('juin', 'June').replace('juillet', 'July').replace('août', 'August').replace('septembre', 'September').replace('octobre', 'October').replace('novembre', 'November').replace('décembre', 'December')
        website_date = datetime.strptime(website_date, '%d/%m').strftime('%d/%m/2023')
    return website_date

def company_news_scraping(company_ticker):
    company_url = company_df[company_df['ticker'] == company_ticker]['url'].values[0]
    url = 'https://www.zonebourse.com/cours/action/' + company_url + '/actualite-historique/'
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'html.parser')
    quotes = []
    table = soup.find('table', attrs={'id': 'ALNI4'})
    for row in table.findAll('tr'):
        try:
            quote = {}
            quote['article'] = row.a.text.replace('\n', '').strip()
            quote['ticker'] = company_ticker
            quote['date'] = convert_date(row.td.text)
            quotes.append(quote)
        except TypeError:
            continue
    return quotes


save_news_in_file(company_news_scraping('AIR'))
save_news_in_file(random_news_scraping())


