"""
This file is the main file for the project. It will run all the other files
"""
import os
from emotrade import app
from emotrade.Setup import download_market_data

if __name__ == '__main__':
    # Run all setup files if not already done

    data = app.d.data_path

    if not os.path.exists(data):
        print('Creating directory ' + data + ' at root of the project')
        os.mkdir(data)

    if not os.path.exists(os.path.join(data, "market_data.csv")):
        print('\nDownloading market data...\n')
        download_market_data()

    if not os.path.exists(os.path.join(data, "news.csv")):
        print('\nYou need to add the `news.csv` file into the ' + data + ' folder\n')
        quit()

    app.run_server(debug=True) #TODO: change to False when deploying

