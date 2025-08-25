import os

import numpy as np
import pandas as pd
from dash import callback, Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from trade.defaults import defaults as dlt


@callback(
    Output("chart", "figure", allow_duplicate=True),
    Input("modify-button-new-graph", "n_clicks"),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('granularity-select', 'value'),
    State("new-graph-df", "data"),
    prevent_initial_call=True
)
def export_to_csv(n, start_date, end_date, granularity, graph_data):
    """Export generated OHLC data to CSV and update defaults.

    On success, writes `generated_data.csv` under `dlt.data_path` and updates
    `start_date` and `granularity` in `trade/defaults.py`.

    Args:
        n (int): Clicks on modify button.
        start_date (str): Selected start date.
        end_date (str): Selected end date.
        granularity (str): Frequency string.
        graph_data (dict): Simplified export payload from preview.

    Returns:
        no_update: Figure is not modified; the export is a side effect.

    Raises:
        PreventUpdate: If `graph_data` is empty.
    """
    if not graph_data:
        raise PreventUpdate

    # --- Mise à jour de trade/defaults.py ---
    defaults_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../defaults.py'))
    if not os.path.isfile(defaults_path):
        import pathlib
        current = pathlib.Path(__file__).resolve()
        for parent in current.parents:
            candidate = parent / 'trade' / 'defaults.py'
            if candidate.exists():
                defaults_path = str(candidate)
                break
    try:
        print(f"[EXPORT] Ouverture de {defaults_path} pour mise à jour")
        with open(defaults_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith('start_date'):
                new_lines.append(f'    start_date = "{start_date}" \n')
            elif line.strip().startswith('granularity'):
                new_lines.append(f'    granularity = "{granularity}" \n')
            else:
                new_lines.append(line)
        with open(defaults_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("[EXPORT] defaults.py mis à jour")
    except Exception as e:
        print(f'[EXPORT] Erreur lors de la mise à jour de defaults.py : {e}')
    # --- Fin mise à jour ---

    try:
        print("[EXPORT] Reconstruction du DataFrame à partir de graph_data")
        df = pd.DataFrame(graph_data['data'])
        print(f"[EXPORT] Colonnes du DataFrame: {df.columns}")
        df.columns = pd.MultiIndex.from_tuples(
            [tuple(col.split('|')) for col in graph_data['column_names']],
            names=['symbol', None]
        )
        print(f"[EXPORT] MultiIndex columns: {df.columns}")
        expected_cols = ['Open', 'High', 'Low', 'Close', 'adjclose', 'Volume', 'long_MA', 'short_MA', '200_MA', 'RSI']
        all_symbols = df.columns.get_level_values('symbol').unique()
        new_cols = []
        for symbol in all_symbols:
            for col in expected_cols:
                new_cols.append((symbol, col))
        for col in new_cols:
            if col not in df.columns:
                df[col] = np.nan
        df = df.reindex(columns=new_cols)
        print(f"[EXPORT] Colonnes après reindex: {df.columns}")
        df.index = pd.to_datetime(graph_data['index'])
        print(f"[EXPORT] Index du DataFrame: {df.index}")
        all_symbols = df.columns.get_level_values('symbol').unique()
        freq = granularity
        all_dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        print(f"[EXPORT] all_dates: {all_dates}")
        df = df.reindex(all_dates)
        generated_data_path = os.path.join(dlt.data_path, 'generated_data.csv')
        print(f"[EXPORT] Sauvegarde du DataFrame dans {generated_data_path}")
        df.to_csv(generated_data_path, index=True)
        print("[EXPORT] Export terminé avec succès !")
        return no_update
    except Exception as e:
        print('Error while exporting to CSV:', e)
        import traceback
        traceback.print_exc()
        return no_update
