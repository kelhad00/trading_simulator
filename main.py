"""
This file is the main file for the project. It will run all the other files
"""
import os
from emotrade import app
from emotrade.Setup import download_market_data, scraping_news

if __name__ == '__main__':
    # Run all setup files if not already done

    if not os.path.exists('Data'):
        print('Creating directory Data at root of the project')
        os.mkdir('Data')

    if not os.path.exists(os.path.join('Data', "market_data.csv")):
        print('\nDownloading market data...\n')
        download_market_data()

    if not os.path.exists(os.path.join('Data', "news.csv")):
        print('\nScrapping news...\n')
        scraping_news()
        print('Done\n')

    app.run_server(debug=True) #TODO: change to False when deploying

