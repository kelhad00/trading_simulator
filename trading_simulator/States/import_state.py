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
    Output('request-list', 'data', allow_duplicate=True),
    Input('price-dataframe', 'data'), # less updated than other components
	State('market-timestamp-value','data'),
    prevent_initial_call=True
)
def import_state(n, timestamp):
    # If information has been imported don't do anything
    if timestamp != '':
        raise PreventUpdate # Exit the callback without updating anything

    file_path = os.path.join('Data', 'interface-logs.csv')
    if not os.path.exists(file_path):
        # If no state has been saved yet,
        # let initialize the app with default values
        raise PreventUpdate
    else:
        # Import the data
        df = pd.read_csv(file_path, on_bad_lines='skip')
        nbr_logs = df.shape[0]
        df = df.iloc[-1]

        # Format imported data to be used in the app
        shares = df[[c + '-shares' for c in COMP.keys()]].to_frame().T.reset_index(drop=True).rename(
            columns={c + '-shares': c for c in COMP.keys()},
            index={0: 'Shares'}
        ).to_dict()

        totals = df[[c + '-total' for c in COMP.keys()]].to_frame().T.reset_index(drop=True).rename(
            columns={c + '-total': c for c in COMP.keys()},
            index={0: 'Total'}
        ).to_dict()

        # Import all requests as strings and split them into lists
        request_list = df[
            ['request '+ str(i + 1) for i in range(MAX_REQUESTS)]
        ].dropna().str.split()
        # Convert requests list elements to the right type
        request_list = [
            # [ action, quantity, company, price ]
            # Example: {Buy} {10} shares of {LVMH} at {100}$
            [ i[0], int(i[1]), i[2], int(i[3]) ] for i in request_list.values
        ]

        return nbr_logs, df['market-timestamp'], df['selected-company'], \
               df['cashflow'], df['last-news-id'], totals, shares, request_list
