import importlib
import importlib.resources as resources
import subprocess
import os
import shutil

"""
Provides scripts files as functions
"""

def download_market_data():
    """ Download market data from Yahoo Finance and save it into a data folder
        You can change the default path and data to download from the trade.defaults variables
    """
    try:
        importlib.import_module('.download_market_data', __package__)
    except ModuleNotFoundError:
        print('\nError while downloading market data.\nPlease make sure you have yahooquery installed and try again.')
        quit()


def analyse_news_data(data_path='Data'):
    """ Open a jupyter notebook to analyse the news data
    """
    notebook_file = "analyze.ipynb"
    working_dir = os.path.join(os.getcwd(), data_path)

    with resources.path(__package__, notebook_file) as path:
        shutil.copy(path, working_dir)

    try:
        cmd = f"jupyter notebook {notebook_file}"
        subprocess.run(cmd, shell=True, cwd=working_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"""
Error while running notebook.
Please make sure you have jupyter installed and try again.
        """)
