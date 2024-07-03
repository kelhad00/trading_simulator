import json
import os
import time
from trade.defaults import defaults as dlt


def create_json():
    file = dict()
    file['timestamp'] = ''
    file['cashflow'] = {
        "lastUpdate": int(time.time()),
        "content": dlt.initial_money
    }
    file['portfolio'] = dict()
    file['portfolio']['shares'] = {
        "lastUpdate": int(time.time()),
        "content": {c: 0 for c in dlt.companies.keys()}
    }
    file['portfolio']['totals'] = {
        "lastUpdate": int(time.time()),
        "content": {c: 0 for c in dlt.companies.keys()}
    }
    file['requests'] = {
        "lastUpdate": int(time.time()),
        "content": []
    }

    with open('../../data-test.json', 'w') as f:
        json.dump(file, f, indent=4)



