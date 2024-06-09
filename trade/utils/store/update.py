import json
import time

path = 'data-test.json'


def update_timestamp(timestamp: str) -> str:
    """ Update the timestamp value in the browser
    """
    with open(path, 'r') as f:
        data = json.load(f)
    data['timestamp'] = timestamp
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return timestamp


def update_cashflow(cashflow: dict) -> dict:
    """ Update the cashflow value in the browser
    """
    with open(path, 'r') as f:
        data = json.load(f)
    data['cashflow']['content'] = cashflow
    data['cashflow']['lastUpdate'] = int(time.time())
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return cashflow

def update_portfolio_shares(portfolio_shares: dict) -> dict:
    """ Update the portfolio shares value in the browser
    """
    with open(path, 'r') as f:
        data = json.load(f)
    data['portfolio']['shares']['content'] = portfolio_shares
    data['portfolio']['shares']['lastUpdate'] = int(time.time())
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return portfolio_shares


def update_portfolio_totals(portfolio_totals: dict) -> dict:
    """ Update the portfolio totals value in the browser
    """
    with open(path, 'r') as f:
        data = json.load(f)
    data['portfolio']['totals']['content'] = portfolio_totals
    data['portfolio']['totals']['lastUpdate'] = int(time.time())
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return portfolio_totals


def update_requests(requests: list) -> list:
    """ Update the requests value in the browser
    """
    with open(path, 'r') as f:
        data = json.load(f)
    data['requests']['content'] = requests
    data['requests']['lastUpdate'] = int(time.time())
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return requests

