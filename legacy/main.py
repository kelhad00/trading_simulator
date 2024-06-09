"""
This file is the main file for the project. It will run all the other files
"""
import os
import subprocess
import threading


from tradesim import app
from tradesim.Setup import download_market_data

def run_dash_app():
    app.set_layout()  # Set the layout of the trade
    app.run_server(debug=False, port=8000)  # Start the trade


if __name__ == '__main__':
    # Run all setup files if not already done

    path = app.d.data_path # Use the default data path

    if not os.path.exists(path):
        print('Creating directory ' + path + ' at root of the project')
        os.mkdir(path)

    if not os.path.exists(os.path.join(path, "market_data.csv"))\
        or not os.path.exists(os.path.join(path, "revenue.csv")):
        print('\nDownloading market data...\n')
        download_market_data()

    if not os.path.exists(os.path.join(path, "news.csv")):
        print('\nYou need to add the `news.csv` file into the ' + path + ' folder\n')
        quit()

    dash_thread = threading.Thread(target=run_dash_app)
    dash_thread.start()

    # subprocess.run(['watchmedo', 'shell-command', '--patterns=*.py', '--recursive', '--command=pkill -f main.py; ./start_server.sh', '.' ])



