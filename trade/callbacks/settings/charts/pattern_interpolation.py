import os
import json
import numpy as np


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
    import random
    import sys
    pattern_dir = os.path.join(dataset_dir, pattern_name)
    print(f"[DEBUG] Recherche dans : {os.path.abspath(pattern_dir)}")
    files = [f for f in os.listdir(pattern_dir) if f.endswith('.json')]
    if not files:
        raise FileNotFoundError(f"Aucun dataset trouvé pour le pattern {pattern_name}")
    # Prendre jusqu'à 25 fichiers aléatoires
    selected_files = random.sample(files, min(25, len(files)))
    for file in selected_files:
        file_path = os.path.join(pattern_dir, file)
        print(f"[DEBUG] Fichier choisi : {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        prices = data["prices"]
        dates = sorted(prices.keys())
        first_date = dates[0]
        print(f"[DEBUG] Exemples de clés dans prices[first_date]: {list(prices[first_date].keys())}")
        ticker = list(prices[first_date].keys())[0].split(", ")[1].strip("')")
        opens_ref = [prices[d][f"('Open', '{ticker}')"] for d in dates]
        highs_ref = [prices[d][f"('High', '{ticker}')"] for d in dates]
        lows_ref = [prices[d][f"('Low', '{ticker}')"] for d in dates]
        closes_ref = [prices[d][f"('Close', '{ticker}')"] for d in dates]
        # Calcul des variations quotidiennes (returns)
        returns = [(closes_ref[i] - closes_ref[i-1]) / closes_ref[i-1] if closes_ref[i-1] != 0 else 0 for i in range(1, len(closes_ref))]
        # Interpolation sur les variations uniquement
        if len(returns) > 1:
            returns_interp = np.interp(np.linspace(0, 1, duree-1), np.linspace(0, 1, len(returns)), returns)
        else:
            returns_interp = [0] * (duree-1)
        # Reconstruction de la série de prix à partir du prix de base et des variations interpolées
        base_price = opens_ref[0]
        closes_final = [base_price]
        for r in returns_interp:
            closes_final.append(closes_final[-1] * (1 + r))
        closes_final = np.array(closes_final[:duree])  # S'assurer de la taille exacte
        # Pour les autres séries (open, high, low), on applique le même ratio de variation que sur close
        open_offset = np.array(opens_ref) - np.array(closes_ref)
        high_offset = np.array(highs_ref) - np.array(closes_ref)
        low_offset = np.array(lows_ref) - np.array(closes_ref)
        # On interpole ces offsets
        open_offset_interp = np.interp(np.linspace(0, 1, duree), np.linspace(0, 1, len(open_offset)), open_offset)
        high_offset_interp = np.interp(np.linspace(0, 1, duree), np.linspace(0, 1, len(high_offset)), high_offset)
        low_offset_interp = np.interp(np.linspace(0, 1, duree), np.linspace(0, 1, len(low_offset)), low_offset)
        opens_final = closes_final + open_offset_interp[:duree]
        highs_final = closes_final + high_offset_interp[:duree]
        lows_final = closes_final + low_offset_interp[:duree]
        # Ajustement amplitude
        min_val = min(opens_final)
        max_val = max(opens_final)
        current_amp = (max_val - min_val) / base_price if base_price != 0 else 1
        factor = amplitude / current_amp if current_amp != 0 else 1
        opens_final = base_price + (opens_final - base_price) * factor
        highs_final = base_price + (highs_final - base_price) * factor
        lows_final = base_price + (lows_final - base_price) * factor
        closes_final = base_price + (closes_final - base_price) * factor
        # Debug info sur tailles
        print(f"[DEBUG] len(opens_final): {len(opens_final)}, len(highs_final): {len(highs_final)}, len(lows_final): {len(lows_final)}, len(closes_final): {len(closes_final)}")
        print(f"[DEBUG] day: {day}, duree: {duree}")
        print(f"[DEBUG] Indices écrits: {list(range(day, day + duree))}")
        # Remplissage avec extension dynamique si besoin
        for i in range(duree):
            idx = day + i
            for arr, arr_final, name in zip(
                [opens, highs, lows, closes],
                [opens_final, highs_final, lows_final, closes_final],
                ["opens", "highs", "lows", "closes"]):
                if idx >= len(arr):
                    missing = idx - len(arr) + 1
                    print(f"[DEBUG] Extension de la liste {name} de {missing} éléments (taille initiale: {len(arr)})")
                    arr.extend([None] * missing)
                arr[idx] = arr_final[i]
        # Contrôle strict de la taille
        if not (len(closes_final) == len(opens_final) == len(highs_final) == len(lows_final) == duree):
            raise ValueError(f"Erreur de cohérence: tailles générées closes={len(closes_final)}, opens={len(opens_final)}, highs={len(highs_final)}, lows={len(lows_final)} != duree={duree}")
        print(f"[DEBUG] TAILLES finales: closes={len(closes_final)}, opens={len(opens_final)}, highs={len(highs_final)}, lows={len(lows_final)}, duree={duree}") 