"""
This file is the main file for the project. It will run all the other files
"""
import os
from trading_simulator import app

# Import data if not already done
if not os.path.exists("Data"):
    # Run all setup files
    print('##### Setup #####'\
        '\nDownloading market data...\n')
    from trading_simulator.Setup import download_market_data

    print('\nScrapping news...\n')
    from trading_simulator.Setup import scraping_with_bs4

    print('\nSetup done')

# Run the app
if __name__ == '__main__':
    print('\n##### Running app #####\n')
    app.run_server(debug=True) #TODO: change to False when deploying

