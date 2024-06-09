import json
import pandas as pd


def get_timestamp():
    try:
        with open('data-test.json', 'r') as f:
            data = json.load(f)
        return data['timestamp']
    except:
        print('ERROR: No data found in data-test.json file.')
        raise FileNotFoundError


def get_cashflow():
    try:
        with open('data-test.json', 'r') as f:
            data = json.load(f)
        return data['cashflow']['content'], data['cashflow']['lastUpdate']
    except:
        print('ERROR: No data found in data-test.json file.')
        raise FileNotFoundError


def get_portfolio_shares():
    try :
        with open('data-test.json', 'r') as f:
            data = json.load(f)
        s = pd.Series(data['portfolio']['shares']['content'])
        return s, data['portfolio']['shares']['lastUpdate']
    except:
        print('ERROR: No data found in data-test.json file.')
        raise FileNotFoundError


def get_portfolio_totals():
    try:
        with open('data-test.json', 'r') as f:
            data = json.load(f)

        s = pd.Series(data['portfolio']['totals']['content'])
        return s, data['portfolio']['totals']['lastUpdate']
    except:
        print('ERROR: No data found in data-test.json file.')
        raise FileNotFoundError


def get_requests():
    try:
        with open('data-test.json', 'r') as f:
            data = json.load(f)
        return data['requests']['content'], data['requests']['lastUpdate']
    except:
        print('ERROR: No data found in data-test.json file.')
        raise FileNotFoundError


def get_portfolio_dataframe():
    shares, date = get_portfolio_shares()
    totals, date = get_portfolio_totals()
    df = pd.concat([shares, totals], axis=1)
    df.columns = ['Shares', 'Totals']
    return df

