import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def insert_bullish_engulfing(opens, highs, lows, closes, day):
    # Jour 1 : bougie rouge
    open1 = opens[day]
    close1 = open1 * 0.995  # petite baisse
    opens[day] = open1
    closes[day] = close1

    # Jour 2 : bougie verte qui englobe la précédente
    open2 = close1 * 0.995  # plus bas que close1
    close2 = open1 * 1.005  # plus haut que open1
    opens[day + 1] = open2
    closes[day + 1] = close2

    # Mèches
    body1_high = max(open1, close1)
    body1_low = min(open1, close1)
    body2_high = max(open2, close2)
    body2_low = min(open2, close2)
    
    delta1 = (body1_high - body1_low) * 0.3
    delta2 = (body2_high - body2_low) * 0.3

    highs[day] = body1_high + delta1
    lows[day] = body1_low - delta1
    highs[day + 1] = body2_high + delta2
    lows[day + 1] = body2_low - delta2


def insert_bearish_engulfing(opens, highs, lows, closes, day):
    # Jour 1 : bougie verte (petite hausse)
    open1 = opens[day]
    close1 = open1 * 1.005  # petite hausse
    opens[day] = open1
    closes[day] = close1

    # Jour 2 : bougie rouge qui englobe la précédente
    open2 = close1 * 1.005  # plus haut que close1
    close2 = open1 * 0.995  # plus bas que open1
    opens[day + 1] = open2
    closes[day + 1] = close2

    # Mèches
    body1_high = max(open1, close1)
    body1_low = min(open1, close1)
    body2_high = max(open2, close2)
    body2_low = min(open2, close2)

    delta1 = (body1_high - body1_low) * 0.3
    delta2 = (body2_high - body2_low) * 0.3

    highs[day] = body1_high + delta1
    lows[day] = body1_low - delta1
    highs[day + 1] = body2_high + delta2
    lows[day + 1] = body2_low - delta2

def insert_hammer(opens, highs, lows, closes, day):
    import numpy as np

    prev_close = closes[day - 1]

    # Définir un petit corps (0.1% à 0.3%)
    body_pct = np.random.uniform(0.001, 0.003)
    direction = np.random.choice([-1, 1])  # marteau rouge ou vert

    opens[day] = prev_close * (1 + np.random.normal(0, 0.0005))
    closes[day] = opens[day] * (1 + direction * body_pct)

    base_price = min(opens[day], closes[day])
    top_price = max(opens[day], closes[day])

    # Ombre inférieure au moins 3x le corps
    body_size = abs(closes[day] - opens[day])
    lows[day] = base_price - body_size * np.random.uniform(3, 4)

    # Petite mèche haute
    highs[day] = top_price + body_size * np.random.uniform(0.05, 0.1)


def insert_shooting_star(opens, highs, lows, closes, day):
    import numpy as np

    prev_close = closes[day - 1]

    # Corps petit (0.1% à 0.3%)
    body_pct = np.random.uniform(0.001, 0.003)
    direction = np.random.choice([-1, 1])  # rouge (souhaité) ou vert (possible)

    opens[day] = prev_close * (1 + np.random.normal(0, 0.0005))
    closes[day] = opens[day] * (1 + direction * body_pct)

    base_price = min(opens[day], closes[day])
    top_price = max(opens[day], closes[day])
    body_size = abs(closes[day] - opens[day])

    # Longue mèche supérieure : 2–3 fois le corps
    highs[day] = top_price + body_size * np.random.uniform(2.5, 3.5)

    # Mèche inférieure quasi inexistante
    lows[day] = base_price - body_size * np.random.uniform(0.05, 0.1)

def insert_double_top(opens, highs, lows, closes, day):
    import numpy as np

    # Base price from previous close
    base_price = closes[day - 1]

    # Premier sommet
    top = base_price * 1.02  # +2%
    creux = base_price * 1.01  # +1%
    
    # Bougie 1 : montée
    opens[day] = base_price
    closes[day] = base_price * 1.015
    
    # Bougie 2 : sommet 1
    opens[day+1] = closes[day]
    closes[day+1] = top

    # Bougie 3 : repli vers creux
    opens[day+2] = closes[day+1]
    closes[day+2] = creux

    # Bougie 4 : second sommet
    opens[day+3] = creux
    closes[day+3] = top * np.random.uniform(0.998, 1.002)  # proche du sommet 1

    # Bougie 5 : chute
    opens[day+4] = closes[day+3]
    closes[day+4] = base_price * 0.99  # cassure du support

    # Mèches
    for i in range(5):
        idx = day + i
        highs[idx] = max(opens[idx], closes[idx]) * np.random.uniform(1.001, 1.003)
        lows[idx] = min(opens[idx], closes[idx]) * np.random.uniform(0.997, 0.999)

def insert_head_and_shoulders(opens, highs, lows, closes, day):
    base_price = closes[day - 1]

    # Niveaux des sommets
    shoulder = base_price * 1.02  # +2%
    head = base_price * 1.04      # +4%
    neckline = base_price * 0.99  # ligne de cou à -1%

    levels = [
        shoulder,    # Épaule gauche
        neckline,    # Retour ligne de cou
        head,        # Tête
        neckline,    # Retour ligne de cou
        shoulder,    # Épaule droite
        base_price * 0.97  # Cassure (signal)
    ]

    for i, level in enumerate(levels):
        idx = day + i
        # Corps simulé aléatoirement autour du niveau
        body_size = level * np.random.uniform(0.002, 0.005)
        direction = np.random.choice([-1, 1])
        opens[idx] = level * (1 - direction * 0.001)
        closes[idx] = opens[idx] + direction * body_size

        # Mèches
        highs[idx] = max(opens[idx], closes[idx]) * np.random.uniform(1.001, 1.003)
        lows[idx] = min(opens[idx], closes[idx]) * np.random.uniform(0.997, 0.999)
