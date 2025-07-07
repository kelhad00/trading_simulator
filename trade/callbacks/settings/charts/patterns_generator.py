import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from .pattern_interpolation import fill_ohlc_from_dataset

def insert_bullish_engulfing(opens, highs, lows, closes, day, amplitude=0.05):
    # Jour 1 : bougie rouge
    open1 = opens[day]
    close1 = open1 * (1 - amplitude)  # amplitude = pourcentage de baisse (ex: 0.01 pour -1%)
    opens[day] = open1
    closes[day] = close1

    # Jour 2 : bougie verte qui englobe la précédente
    open2 = close1 * (1 - amplitude)  # plus bas que close1
    close2 = open1 * (1 + amplitude)  # plus haut que open1

    insert_engulfing_details(opens, highs, lows, closes, day, open1, close1, open2, close2)


def insert_bearish_engulfing(opens, highs, lows, closes, day, amplitude=0.05):
    # Jour 1 : bougie verte (petite hausse)
    open1 = opens[day]
    close1 = open1 * (1 + amplitude)  # petite hausse
    opens[day] = open1
    closes[day] = close1

    # Jour 2 : bougie rouge qui englobe la précédente
    open2 = close1 * (1 + amplitude) # plus haut que close1
    close2 = open1 * (1 - amplitude)  # plus bas que open1

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

def insert_hammer(opens, highs, lows, closes, day, amplitude=0.002):
    # amplitude = pourcentage du corps (ex: 0.002 pour 0.2%)
    direction = 1
    opens[day] = closes[day - 1] * (1 + np.random.normal(0, 0.0005))
    closes[day] = opens[day] * (1 + direction * amplitude)
    base_price = min(opens[day], closes[day])
    top_price = max(opens[day], closes[day])
    body_size = abs(closes[day] - opens[day])
    lows[day] = base_price - body_size * np.random.uniform(3, 4)
    highs[day] = top_price + body_size * np.random.uniform(0.05, 0.1)


def insert_shooting_star(opens, highs, lows, closes, day, amplitude=0.002):
    # amplitude = pourcentage du corps (ex: 0.002 pour 0.2%)
    direction = -1
    opens[day] = closes[day - 1] * (1 + np.random.normal(0, 0.0005))
    closes[day] = opens[day] * (1 + direction * amplitude)
    base_price = min(opens[day], closes[day])
    top_price = max(opens[day], closes[day])
    body_size = abs(closes[day] - opens[day])
    highs[day] = top_price + body_size * np.random.uniform(2.5, 3.5)
    lows[day] = base_price - body_size * np.random.uniform(0.05, 0.1)

def insert_double_top(opens, highs, lows, closes, day, amplitude=0.02, duree=5):
    fill_ohlc_from_dataset(opens, highs, lows, closes, day, 'Double_Top', amplitude, duree)

def insert_head_and_shoulders(opens, highs, lows, closes, day, amplitude=0.02, duree=6):
    fill_ohlc_from_dataset(opens, highs, lows, closes, day, 'Head_and_Shoulders', amplitude, duree)

def insert_double_bottom(opens, highs, lows, closes, day, amplitude=0.02, duree=5):
    fill_ohlc_from_dataset(opens, highs, lows, closes, day, 'Double_Bottom', amplitude, duree)

def insert_inverse_head_and_shoulders(opens, highs, lows, closes, day, amplitude=0.02, duree=6):
    fill_ohlc_from_dataset(opens, highs, lows, closes, day, 'Inverse_Head_and_Shoulders', amplitude, duree)
