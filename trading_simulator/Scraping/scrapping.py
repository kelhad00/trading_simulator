from bs4 import BeautifulSoup
import requests
import os
import pandas as pd
import csv
from datetime import datetime
from trading_simulator.Scraping.company_scraping import titles_scraping, articles_scraping, date_scraping

# dataframe with the 20 first companies of the cac40 and their url
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

# Save the table all_articles that contains the title, the content, the ticker and the date of the news
#
# all_articles = []
# def save_dataset_in_file(datas):
#     filename = 'news.csv'
#     df = pd.DataFrame(datas)
#     # append the new data to the old file
#     df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';', mode='a')
#     df = pd.read_csv(filename, sep=';')
#     # delete the second header
#     df = df[df['title'] != 'title']
#     # delete the duplicates
#     df = df.drop_duplicates()
#     # save the new data
#     df.to_csv(filename, index=False, encoding='utf-8-sig', sep=';')
#     return print('File saved')

# TODO: tmp solution to fix the header problem
# create the header of the dataset
def create_news_file_header(filename):
    path = os.path.join('Data', filename)
    with open(path, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['article', 'ticker', 'date'])
    return 0

# save the current news in the file
def save_news_in_file(news, filename):
    path = os.path.join('Data', filename)
    with open(path, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        # writer.writerow([news['title'], news['content'], news['ticker'], news['date']])
        writer.writerow([news['title'], news['ticker'], news['date']])
    return 0


# This function scrap the last news that are published on the website zonebourse.com
# 'max_date' is the date until the scraping is done
def random_news_scraping(max_date):
    article = {}
    page_index = 1
    # date of the article that is currently scraped
    current_date = datetime.now().strftime("%d/%m/%Y")
    # Write dataset header before scraping
    create_news_file_header('news.csv')
    # Scraping loop
    while compare_date(current_date) > compare_date(max_date):
        # number of the current page
        print('Current page = ' + str(page_index))
        # url of the current page
        random_url = "https://www.zonebourse.com/actualite-bourse/societes/?p=" + str(page_index)
        random_request = requests.get(random_url)
        random_soup = BeautifulSoup(random_request.content, 'html.parser')
        # Scraping the table that contains the news
        random_table = random_soup.find('table', attrs={'id': 'newsScreener'})
        for row in random_table.findAll('tr', attrs={'class': '""'}):
            try:
                # scrap the title, the content, the ticker and the date of the news
                article['title'] = row.a.text.replace('\n', '').strip()
                article['ticker'] = row.span.text.replace('\n', '').strip()
                article['date'] = row.time['title']
                # save the date of the current article
                current_date = article['date'].split(' ')[1]
                # check if the date of the current article is before the date until scraping
                if compare_date(date_until_scrap) > compare_date(current_date):
                    break
                # all_articles.append(article)
                save_news_in_file(article, 'random_companies_scrap.csv')
            except TypeError:
                continue
        page_index += 1

        # Fix scraping error starting from page 100
        # TODO: replace this fix by a better solution
        if page_index == 101:
            break
    return 1


# This function scrap the news of a specific company from the data frame 'company_df'
# 'company_ticker' is the ticker of the company, 'date_until_scrap' is the date until the scraping is done
def company_news_scraping(company_ticker, date_until_scrap):
    # get the url of the company
    company_url = company_df[company_df['ticker'] == company_ticker]['url'].values[0]
    # date of the article that is currently scraped
    current_date = datetime.now().strftime("%d/%m/%Y")
    page_index = 1
    print ('Scraping of ' + company_df[company_df['ticker'] == company_ticker]['name'].values[0] + 'news')
    # Scraping loop
    while compare_date(date_until_scrap) < compare_date(current_date):
        print('Page ' + str(page_index))
        # url of the current page of the company
        url = 'https://www.zonebourse.com/cours/action/' + company_url + '/actualite-historique/&nbstrat=0&&fpage=' + str(page_index)
        request = requests.get(url)
        soup = BeautifulSoup(request.content, 'html.parser')
        # Scraping the table that contains the news
        table = soup.find('table', attrs={'id': 'ALNI4'})
        for row in table.findAll('tr'):
            try:
                # scrap the title, the content, the ticker and the date of the news
                article = {}
                article['title'] = titles_scraping(row.a['href']).replace('\n', '').strip()
                # article['content'] = articles_scraping(row.a['href']).replace('\n\n', '\n')
                article['content'] = 'Null'
                article['ticker'] = company_ticker
                article['date'] = date_scraping(row.a['href'])
                # save the date of the current article
                current_date = str(article['date']).split(' ')[0]
                # all_articles.append(article)
                # check if the date of the current article is before the date until scraping
                if compare_date(date_until_scrap) > compare_date(current_date):
                    break
                # save the article in the file
                # save_news_in_file(article, company_ticker + '_scraping.csv')
                save_news_in_file(article, 'companies_scraping.csv')
            except TypeError:
                continue
        page_index += 1
    return 1


if __name__ == '__main__':
    # save_news_in_file(random_news_scraping("MC"))
    for company in cac40data:
        company_news_scraping(company[1], '01/06/2023')
    # company_news_scraping("AIR", '04/06/2023')
    # random_news_scraping('20/05/2023')