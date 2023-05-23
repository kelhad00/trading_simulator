"""
This file is the main file for the project. It will run all the other files
"""
import os

# Import data if not already done
if not os.path.exists("Data"):
    # Run all setup files
    print('##### Setup #####'\
        '\nDownloading market data...\n')
    from Setup import download_market_data

    print('\nDownloading news...\n')
    from Setup import download_news

    print('\nSetup done')

# Run the app
print('\n##### Running app #####\n')
os.system('python app.py')

