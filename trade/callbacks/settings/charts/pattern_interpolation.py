import os
import json
import numpy as np
import random


def interpolate_series(series, target_len):
    x_old = np.linspace(0, 1, len(series))
    x_new = np.linspace(0, 1, target_len)
    return np.interp(x_new, x_old, series)


def scale_amplitude(series, amplitude, base_price):
    min_val = min(series)
    max_val = max(series)
    current_amp = (max_val - min_val) / base_price if base_price != 0 else 1
    factor = amplitude / current_amp if current_amp != 0 else 1
    return [base_price + (v - base_price) * factor for v in series]


def fill_ohlc_from_dataset(opens, highs, lows, closes, day, pattern_name, amplitude, duree, dataset_dir="../data/dataset"):
    """
    Remplit les tableaux OHLC à partir d'un fichier dataset du pattern donné, interpolé à la durée et amplitude demandées.
    """
    import sys
    pattern_dir = os.path.join(dataset_dir, pattern_name)
    files = [f for f in os.listdir(pattern_dir) if f.endswith('.json')]
    if not files:
        raise FileNotFoundError(f"Aucun dataset trouvé pour le pattern {pattern_name}")
    # Prendre un fichier au hasard
    file = random.choice(files)
    file_path = os.path.join(pattern_dir, file)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    prices = data["prices"]
    dates = sorted(prices.keys())
    first_date = dates[0]
    ticker = list(prices[first_date].keys())[0].split(", ")[1].strip("')")
    opens_ref = [prices[d][f"('Open', '{ticker}')"] for d in dates]
    highs_ref = [prices[d][f"('High', '{ticker}')"] for d in dates]
    lows_ref = [prices[d][f"('Low', '{ticker}')"] for d in dates]
    closes_ref = [prices[d][f"('Close', '{ticker}')"] for d in dates]
    # Interpolation directe des séries pour respecter la durée demandée
    def interp(series, target_len):
        if len(series) == target_len:
            return np.array(series)
        return np.interp(np.linspace(0, 1, target_len), np.linspace(0, 1, len(series)), series)
    opens_final = interp(opens_ref, duree)
    highs_final = interp(highs_ref, duree)
    lows_final = interp(lows_ref, duree)
    closes_final = interp(closes_ref, duree)
    # Ajustement amplitude
    base_price = opens_final[0]
    min_val = min(opens_final)
    max_val = max(opens_final)
    current_amp = (max_val - min_val) / base_price if base_price != 0 else 1
    factor = amplitude / current_amp if current_amp != 0 else 1
    opens_final = base_price + (opens_final - base_price) * factor
    highs_final = base_price + (highs_final - base_price) * factor
    lows_final = base_price + (lows_final - base_price) * factor
    closes_final = base_price + (closes_final - base_price) * factor
    # Remplissage avec extension dynamique si besoin
    for i in range(duree):
        idx = day + i
        for arr, arr_final, name in zip(
            [opens, highs, lows, closes],
            [opens_final, highs_final, lows_final, closes_final],
            ["opens", "highs", "lows", "closes"]):
            if idx >= len(arr):
                missing = idx - len(arr) + 1
                arr.extend([None] * missing)
            arr[idx] = arr_final[i]
    # Contrôle strict de la taille
    if not (len(closes_final) == len(opens_final) == len(highs_final) == len(lows_final) == duree):
        raise ValueError(f"Erreur de cohérence: tailles générées closes={len(closes_final)}, opens={len(opens_final)}, highs={len(highs_final)}, lows={len(lows_final)} != duree={duree}")
