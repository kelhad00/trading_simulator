from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
from tqdm import tqdm
from company_scraping import titles_scraping, articles_scraping, date_scraping
from datetime import datetime

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
        # writer.writerow([news['title'], news['content'], news['ticker'], news['date']])
        writer.writerow([news['title'], news['ticker'], news['date']])
    return 0


def random_news_scraping(max_date):
    # for page_index in tqdm(range(1, number_of_pages_to_scrap + 1)):
    quote = {}
    page_index = 1
    current_date = datetime.now().strftime("%d/%m/%Y")
    while current_date != max_date:
        print('Current page = ' + str(page_index))
        random_url = "https://www.zonebourse.com/actualite-bourse/societes/?p=" + str(page_index) + "&cf=RWJlMUV1N3NMRitwYlUxRG9PUjZibnBDZmtYRzJ3dHplQU1rR0pscTJVbz0"
        random_request = requests.get(random_url)
        random_soup = BeautifulSoup(random_request.content, 'html.parser')
        random_table = random_soup.find('table', attrs={'id': 'newsScreener'})
        for row in random_table.findAll('tr', attrs={'class': '""'}):
            try:
                quote['title'] = row.a.text.replace('\n', '').strip()
                # quote['content'] = articles_scraping(row.a['href'])
                quote['ticker'] = row.span.text.replace('\n', '').strip()
                quote['date'] = row.time['title']
                current_date = quote['date'].split(' ')[1]
                # quotes.append(quote)
                save_news_in_file(quote, 'random_companies_scrap.csv')
            except TypeError:
                continue
        page_index += 1
    return quotes

def company_news_scraping(company_ticker, pages_number_to_scrap):
    company_url = company_df[company_df['ticker'] == company_ticker]['url'].values[0]
    for i in tqdm(range(1, pages_number_to_scrap + 1)):
        print('Page ' + str(i))
        url = 'https://www.zonebourse.com/cours/action/' + company_url + '/actualite-historique/&nbstrat=0&&fpage=' + str(i)
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')
        table = soup.find('table', attrs={'id': 'ALNI4'})
        for row in table.findAll('tr'):
            try:
                quote = {}
                quote['title'] = titles_scraping(row.a['href']).replace('\n', '').strip()
                # quote['content'] = articles_scraping(row.a['href']).replace('\n\n', '\n')
                quote['content'] = 'Null'
                quote['ticker'] = company_ticker
                quote['date'] = date_scraping(row.a['href'])
                # quotes.append(quote)
                save_news_in_file(quote, 'test.csv')
            except TypeError:
                continue
    return quotes


# save_news_in_file(random_news_scraping("MC"))
# company_news_scraping("MC", 4)
random_news_scraping('30/04/2023')