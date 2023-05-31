import os
import numpy as np
import pandas as pd
from dash import Output, Input, State
from dash.exceptions import PreventUpdate

from trading_simulator import COMP, MAX_REQUESTS
from trading_simulator.app import app


@app.callback(
	Output('nbr-logs', 'data', allow_duplicate=True),
    Output('market-timestamp-value','data', allow_duplicate=True),
    Output('company-selector', 'value', allow_duplicate=True),
	Output('cashflow', 'data', allow_duplicate=True),
	Output('news-index', 'data', allow_duplicate=True),
	Output('portfolio_totals', 'data', allow_duplicate=True),
	Output('portfolio_shares', 'data', allow_duplicate=True),
    # Output('request-list', 'data', allow_duplicate=True),
    Input('price-dataframe', 'data'), # less updated than other components
	State('market-timestamp-value','data'),
    prevent_initial_call=True
)
def import_state(n, timestamp):
    # If information has been imported don't do anything
    if timestamp != '':
        PreventUpdate()

    file_path = os.path.join('Data', 'interface-logs.csv')
    if not os.path.exists(file_path):
        PreventUpdate()
    else:
        # Import the data
        df = pd.read_csv(file_path, on_bad_lines='skip')
        nbr_logs = df.shape[0]
        df = df.iloc[-1]

        shares = df[[c + '-shares' for c in COMP.keys()]].to_frame().T.reset_index(drop=True).rename(
            columns={c + '-shares': c for c in COMP.keys()},
            index={0: 'Shares'}
        ).to_dict()

        totals = df[[c + '-total' for c in COMP.keys()]].to_frame().T.reset_index(drop=True).rename(
            columns={c + '-total': c for c in COMP.keys()},
            index={0: 'Total'}
        ).to_dict()

        # tmp = df[['request '+ str(i + 1) for i in range(MAX_REQUESTS)]].dropna().s.str.split()

        print(shares)
        print(totals)

        return nbr_logs, df['market-timestamp'], df['selected-company'], \
               df['cashflow'], df['last-news-id'], totals, shares
