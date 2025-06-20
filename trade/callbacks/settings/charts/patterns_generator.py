import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def insert_bullish_engulfing(opens, highs, lows, closes, day, down1 = 0.995, up1 = 1.005):
    # Jour 1 : bougie rouge
    open1 = opens[day]
    close1 = open1 * down1  # petite baisse
    opens[day] = open1
    closes[day] = close1

    # Jour 2 : bougie verte qui englobe la précédente
    open2 = close1 * down1  # plus bas que close1
    close2 = open1 * up1  # plus haut que open1

    insert_engulfing_details(opens, highs, lows, closes, day, open1, close1, open2, close2)


def insert_bearish_engulfing(opens, highs, lows, closes, day, down1 = 0.995, up1 = 1.005):
    # Jour 1 : bougie verte (petite hausse)
    open1 = opens[day]
    close1 = open1 * up1  # petite hausse
    opens[day] = open1
    closes[day] = close1

    # Jour 2 : bougie rouge qui englobe la précédente
    open2 = close1 * up1 # plus haut que close1
    close2 = open1 * down1  # plus bas que open1

    insert_engulfing_details(opens, highs, lows, closes, day, open1, close1, open2, close2)

def insert_engulfing_details(opens, highs, lows, closes, day, open1, close1, open2, close2):
    # Assignation des valeurs du jour 2
    opens[day + 1] = open2
    closes[day + 1] = close2

    # Mèches jour 1
    body1_high = max(open1, close1)
    body1_low = min(open1, close1)
    delta1 = (body1_high - body1_low) * 0.3
    highs[day] = body1_high + delta1
    lows[day] = body1_low - delta1

    # Mèches jour 2
    body2_high = max(open2, close2)
    body2_low = min(open2, close2)
    delta2 = (body2_high - body2_low) * 0.3
    highs[day + 1] = body2_high + delta2
    lows[day + 1] = body2_low - delta2

def insert_hammer(opens, highs, lows, closes, day, low = 0.001, high = 0.003):

    # Définir un petit corps (0.1% à 0.3%)
    body_pct = np.random.uniform(low, high)
    direction = 1

    opens[day] = closes[day - 1] * (1 + np.random.normal(0, 0.0005))
    closes[day] = opens[day] * (1 + direction * body_pct)

    base_price = min(opens[day], closes[day])
    top_price = max(opens[day], closes[day])

    # Ombre inférieure au moins 3x le corps
    body_size = abs(closes[day] - opens[day])
    lows[day] = base_price - body_size * np.random.uniform(3, 4)

    # Petite mèche haute
    highs[day] = top_price + body_size * np.random.uniform(0.05, 0.1)


def insert_shooting_star(opens, highs, lows, closes, day, low = 0.001, high = 0.003):

    # Corps petit (0.1% à 0.3%)
    body_pct = np.random.uniform(low, high)
    direction = -1

    opens[day] = closes[day - 1] * (1 + np.random.normal(0, 0.0005))
    closes[day] = opens[day] * (1 + direction * body_pct)

    base_price = min(opens[day], closes[day])
    top_price = max(opens[day], closes[day])
    body_size = abs(closes[day] - opens[day])

    # Longue mèche supérieure : 2–3 fois le corps
    highs[day] = top_price + body_size * np.random.uniform(2.5, 3.5)

    # Mèche inférieure quasi inexistante
    lows[day] = base_price - body_size * np.random.uniform(0.05, 0.1)

def insert_double_top(opens, highs, lows, closes, day, top_init = 1.02, creux_init = 1.01, rise1 = 1.015, low4 = 0.998, high4 = 1.002, close5 = 0.99):
    import numpy as np

    # Base price from previous close
    base_price = closes[day - 1]

    # Premier sommet
    top = base_price * top_init
    creux = base_price * creux_init
    
    # Bougie 1 : montée
    opens[day] = base_price
    closes[day] = base_price * rise1
    
    # Bougie 2 : sommet 1
    opens[day+1] = closes[day]
    closes[day+1] = top

    # Bougie 3 : repli vers creux
    opens[day+2] = closes[day+1]
    closes[day+2] = creux

    # Bougie 4 : second sommet
    opens[day+3] = creux
    closes[day+3] = top * np.random.uniform(low4, high4)  # proche du sommet 1

    # Bougie 5 : chute
    opens[day+4] = closes[day+3]
    closes[day+4] = base_price * close5  # cassure du support

    # Mèches
    for i in range(5):
        idx = day + i
        highs[idx] = max(opens[idx], closes[idx]) * np.random.uniform(1.001, 1.003)
        lows[idx] = min(opens[idx], closes[idx]) * np.random.uniform(0.997, 0.999)

def insert_head_and_shoulders(opens, highs, lows, closes, day, shoulder_rate = 1.02, head_rate = 1.04, neckline_rate = 0.99, breaking_rate = 0.97):
    base_price = closes[day - 1]

    # Définir les niveaux clés
    shoulder = base_price * shoulder_rate
    head = base_price * head_rate
    neckline = base_price * neckline_rate
    breaking = base_price * breaking_rate

    # Bougie 1 : montée vers épaule gauche
    opens[day] = base_price
    closes[day] = shoulder

    # Bougie 2 : baisse vers ligne de cou
    opens[day+1] = closes[day]
    closes[day+1] = neckline

    # Bougie 3 : forte hausse vers tête
    opens[day+2] = closes[day+1]
    closes[day+2] = head

    # Bougie 4 : retour rapide à la ligne de cou
    opens[day+3] = closes[day+2]
    closes[day+3] = neckline

    # Bougie 5 : rebond vers épaule droite (plus bas que la tête)
    opens[day+4] = closes[day+3]
    closes[day+4] = shoulder * np.random.uniform(0.995, 1.005)

    # Bougie 6 : cassure sous la ligne de cou
    opens[day+5] = closes[day+4]
    closes[day+5] = breaking

    # Mèches réalistes
    for i in range(6):
        idx = day + i
        body_high = max(opens[idx], closes[idx])
        body_low = min(opens[idx], closes[idx])
        delta = (body_high - body_low) * np.random.uniform(0.2, 0.4) + 0.0001
        highs[idx] = body_high + delta
        lows[idx] = body_low - delta
