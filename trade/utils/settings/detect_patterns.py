"""
detect_patterns.py
==================
One-time script that scans CAC40.csv for real occurrences of each technical
chart pattern and saves matching windows as CSV files under data/patterns/.

Run from the trading_simulator/trade/ directory:
    python utils/settings/detect_patterns.py
"""

import os
import numpy as np
import pandas as pd

DATA_PATH     = '../data'
PATTERNS_PATH = os.path.join(DATA_PATH, 'patterns')
CAC40_PATH    = os.path.join(DATA_PATH, 'CAC40.csv')
TARGET        = 6   # examples to save per pattern type
SMOOTH_W      = 5   # smoothing window used for peak/trough detection


# ── Helpers ───────────────────────────────────────────────────────────────────

def smooth(arr, w=SMOOTH_W):
    return pd.Series(arr).rolling(w, center=True, min_periods=1).mean().values


def find_peaks(arr, min_dist=8):
    """Local maxima with a minimum bar separation."""
    out = []
    for i in range(1, len(arr) - 1):
        if arr[i] >= arr[i - 1] and arr[i] >= arr[i + 1]:
            if not out or i - out[-1] >= min_dist:
                out.append(i)
            elif arr[i] > arr[out[-1]]:
                out[-1] = i   # replace with higher peak when within min_dist
    return out


def find_troughs(arr, min_dist=8):
    """Local minima with a minimum bar separation."""
    out = []
    for i in range(1, len(arr) - 1):
        if arr[i] <= arr[i - 1] and arr[i] <= arr[i + 1]:
            if not out or i - out[-1] >= min_dist:
                out.append(i)
            elif arr[i] < arr[out[-1]]:
                out[-1] = i
    return out


def slope_normalized(indices, values):
    """Linear regression slope, normalized by the mean value so it is
    comparable across different price levels."""
    x = np.array(indices, dtype=float)
    y = np.array(values,  dtype=float)
    x -= x.mean()
    raw = float(np.dot(x, y) / (np.dot(x, x) + 1e-12))
    return raw / (np.mean(y) + 1e-12)


def no_overlap(saved, s, e, gap=15):
    return all(e < a - gap or s > b + gap for a, b in saved)


def save_window(df, pattern_type, idx, s, e):
    folder = os.path.join(PATTERNS_PATH, pattern_type)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, 'pattern%d.csv' % idx)
    df.iloc[s:e].reset_index(drop=True).to_csv(path, index=False)
    return path


# ── Pattern detectors ─────────────────────────────────────────────────────────

def detect_head_and_shoulders(df, sp, target):
    """Three peaks: shoulders roughly equal, head tallest."""
    peaks = find_peaks(sp, min_dist=10)
    found, saved = [], []
    for i in range(len(peaks) - 2):
        if len(found) >= target:
            break
        p1, p2, p3 = peaks[i], peaks[i + 1], peaks[i + 2]
        h1, h2, h3 = sp[p1], sp[p2], sp[p3]
        if not (h2 > h1 and h2 > h3):
            continue
        if abs(h1 - h3) / h2 > 0.12:              # shoulders within 12%
            continue
        if (h2 - max(h1, h3)) / h2 < 0.03:        # head >= 3% above shoulders
            continue
        if p3 - p1 < 20:
            continue
        s, e = max(0, p1 - 5), min(len(df), p3 + 10)
        if not no_overlap(saved, s, e):
            continue
        found.append((s, e))
        saved.append((s, e))
    return found


def detect_inverse_head_and_shoulders(df, sp, target):
    """Three troughs: shoulders roughly equal, head lowest."""
    troughs = find_troughs(sp, min_dist=10)
    found, saved = [], []
    for i in range(len(troughs) - 2):
        if len(found) >= target:
            break
        t1, t2, t3 = troughs[i], troughs[i + 1], troughs[i + 2]
        h1, h2, h3 = sp[t1], sp[t2], sp[t3]
        if not (h2 < h1 and h2 < h3):
            continue
        if abs(h1 - h3) / max(h1, h3) > 0.12:
            continue
        if (min(h1, h3) - h2) / min(h1, h3) < 0.03:
            continue
        if t3 - t1 < 20:
            continue
        s, e = max(0, t1 - 5), min(len(df), t3 + 10)
        if not no_overlap(saved, s, e):
            continue
        found.append((s, e))
        saved.append((s, e))
    return found


def detect_ascending_triangle(df, sp, target):
    """Flat resistance + strictly rising support."""
    found, saved = [], []
    for s in range(0, len(df) - 35, 2):
        if len(found) >= target:
            break
        for wlen in range(30, 90, 5):
            e = s + wlen
            if e > len(df):
                break
            seg     = sp[s:e]
            peaks   = find_peaks(seg,   min_dist=6)
            troughs = find_troughs(seg, min_dist=6)
            if len(peaks) < 2 or len(troughs) < 2:
                continue
            ph = [seg[p] for p in peaks]
            th = [seg[t] for t in troughs]
            # Flat resistance: all peaks within 4% of each other
            if (max(ph) - min(ph)) / max(ph) > 0.04:
                continue
            # All troughs strictly rising
            if not all(th[i] < th[i + 1] for i in range(len(th) - 1)):
                continue
            # Support slope normalized > 0
            if slope_normalized(troughs, th) <= 0:
                continue
            if not no_overlap(saved, s, e):
                continue
            found.append((s, e))
            saved.append((s, e))
            break
    return found


def detect_descending_triangle(df, sp, target):
    """Flat support + strictly falling resistance."""
    found, saved = [], []
    for s in range(0, len(df) - 35, 2):
        if len(found) >= target:
            break
        for wlen in range(30, 90, 5):
            e = s + wlen
            if e > len(df):
                break
            seg     = sp[s:e]
            peaks   = find_peaks(seg,   min_dist=6)
            troughs = find_troughs(seg, min_dist=6)
            if len(peaks) < 2 or len(troughs) < 2:
                continue
            ph = [seg[p] for p in peaks]
            th = [seg[t] for t in troughs]
            # Flat support: troughs within 4%
            if (max(th) - min(th)) / max(th) > 0.04:
                continue
            # All peaks strictly falling
            if not all(ph[i] > ph[i + 1] for i in range(len(ph) - 1)):
                continue
            if slope_normalized(peaks, ph) >= 0:
                continue
            if not no_overlap(saved, s, e):
                continue
            found.append((s, e))
            saved.append((s, e))
            break
    return found


def detect_bullish_flag(df, sp, target):
    """Sharp upward rally (pole) then tight downward/sideways consolidation."""
    found, saved = [], []
    for s in range(0, len(df) - 25, 2):
        if len(found) >= target:
            break
        for wlen in range(20, 65, 5):
            e = s + wlen
            if e > len(df):
                break
            seg      = sp[s:e]
            pole_end = max(3, wlen // 3)
            pole     = seg[:pole_end]
            flag     = seg[pole_end:]
            if len(flag) < 5:
                continue
            # Pole: strong upward move >= 4%
            if (pole[-1] - pole[0]) / pole[0] < 0.04:
                continue
            # Flag range <= 40% of pole move
            pole_move  = pole[-1] - pole[0]
            flag_range = max(flag) - min(flag)
            if flag_range > 0.40 * pole_move:
                continue
            # Flag slope: downward or flat (not rising more than 0.1% per bar)
            if slope_normalized(range(len(flag)), flag) > 0.001:
                continue
            if not no_overlap(saved, s, e):
                continue
            found.append((s, e))
            saved.append((s, e))
            break
    return found


def detect_bearish_flag(df, sp, target):
    """Sharp downward decline (pole) then tight upward/sideways consolidation."""
    found, saved = [], []
    for s in range(0, len(df) - 25, 2):
        if len(found) >= target:
            break
        for wlen in range(20, 70, 5):
            e = s + wlen
            if e > len(df):
                break
            seg      = sp[s:e]
            pole_end = max(3, wlen // 3)
            pole     = seg[:pole_end]
            flag     = seg[pole_end:]
            if len(flag) < 5:
                continue
            # Pole: downward move >= 3%  (relaxed to find more examples)
            if (pole[0] - pole[-1]) / pole[0] < 0.03:
                continue
            # Flag range <= 55% of pole move  (relaxed)
            pole_move  = pole[0] - pole[-1]
            flag_range = max(flag) - min(flag)
            if flag_range > 0.55 * pole_move:
                continue
            # Flag slope: upward or flat
            if slope_normalized(range(len(flag)), flag) < -0.001:
                continue
            if not no_overlap(saved, s, e):
                continue
            found.append((s, e))
            saved.append((s, e))
            break
    return found


def detect_cup_and_handle(df, sp, target):
    """U-shaped cup followed by a small pullback handle."""
    found, saved = [], []
    for s in range(0, len(df) - 45, 3):
        if len(found) >= target:
            break
        for wlen in range(40, 110, 5):
            e = s + wlen
            if e > len(df):
                break
            seg   = sp[s:e]
            n     = len(seg)
            rim_w = max(4, n // 7)

            left_rim  = float(np.mean(seg[:rim_w]))
            right_rim = float(np.mean(seg[n - rim_w * 2:n - rim_w]))
            handle    = seg[n - rim_w:]
            cup_body  = seg[rim_w:n - rim_w * 2]

            if len(cup_body) < 8:
                continue
            cup_min = float(min(cup_body))

            # Rims roughly equal (within 8%)
            if abs(left_rim - right_rim) / left_rim > 0.08:
                continue
            # Cup depth 8–40%
            depth = (left_rim - cup_min) / left_rim
            if not (0.08 < depth < 0.40):
                continue
            # Handle: small range (< 50% of cup depth in price terms)
            handle_range = max(handle) - min(handle)
            if handle_range > 0.5 * depth * left_rim:
                continue
            # Handle dips (starts near right rim, goes down slightly)
            if handle[0] < right_rim * 0.95:
                continue
            if not no_overlap(saved, s, e):
                continue
            found.append((s, e))
            saved.append((s, e))
            break
    return found


def detect_rising_wedge(df, sp, target):
    """Both peaks and troughs rising, support rising faster (lines converge up)."""
    found, saved = [], []
    for s in range(0, len(df) - 30, 2):
        if len(found) >= target:
            break
        for wlen in range(25, 80, 5):
            e = s + wlen
            if e > len(df):
                break
            seg     = sp[s:e]
            peaks   = find_peaks(seg,   min_dist=6)
            troughs = find_troughs(seg, min_dist=6)
            if len(peaks) < 2 or len(troughs) < 2:
                continue
            ph = [seg[p] for p in peaks]
            th = [seg[t] for t in troughs]
            sl_p = slope_normalized(peaks,   ph)
            sl_t = slope_normalized(troughs, th)
            # Both rising
            if sl_p <= 0 or sl_t <= 0:
                continue
            # Support rises faster than resistance (converging)
            if sl_t <= sl_p * 1.1:
                continue
            # Overall upward price movement
            if seg[-1] <= seg[0]:
                continue
            if not no_overlap(saved, s, e):
                continue
            found.append((s, e))
            saved.append((s, e))
            break
    return found


def detect_falling_wedge(df, sp, target):
    """Both peaks and troughs falling, resistance falling faster (lines converge down)."""
    found, saved = [], []
    for s in range(0, len(df) - 30, 2):
        if len(found) >= target:
            break
        for wlen in range(25, 80, 5):
            e = s + wlen
            if e > len(df):
                break
            seg     = sp[s:e]
            peaks   = find_peaks(seg,   min_dist=6)
            troughs = find_troughs(seg, min_dist=6)
            if len(peaks) < 2 or len(troughs) < 2:
                continue
            ph = [seg[p] for p in peaks]
            th = [seg[t] for t in troughs]
            sl_p = slope_normalized(peaks,   ph)
            sl_t = slope_normalized(troughs, th)
            # Both falling
            if sl_p >= 0 or sl_t >= 0:
                continue
            # Resistance falls faster (more negative slope, converging)
            if sl_p >= sl_t * 1.1:
                continue
            # Overall downward price movement
            if seg[-1] >= seg[0]:
                continue
            if not no_overlap(saved, s, e):
                continue
            found.append((s, e))
            saved.append((s, e))
            break
    return found


# ── Registry ──────────────────────────────────────────────────────────────────

DETECTORS = {
    'head_and_shoulders':         detect_head_and_shoulders,
    'inverse_head_and_shoulders': detect_inverse_head_and_shoulders,
    'ascending_triangle':         detect_ascending_triangle,
    'descending_triangle':        detect_descending_triangle,
    'bullish_flag':               detect_bullish_flag,
    'bearish_flag':               detect_bearish_flag,
    'cup_and_handle':             detect_cup_and_handle,
    'rising_wedge':               detect_rising_wedge,
    'falling_wedge':              detect_falling_wedge,
}


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print('Loading %s ...' % CAC40_PATH)
    df = pd.read_csv(CAC40_PATH).dropna().reset_index(drop=True)
    sp = smooth(df['Close'].values)
    print('  %d rows  |  price range %.0f - %.0f' % (
        len(df), df['Close'].min(), df['Close'].max()))

    total_saved = 0
    for pattern_type, detector in DETECTORS.items():
        print('\n--- %s ---' % pattern_type)
        windows = detector(df, sp, TARGET)
        if not windows:
            print('  No examples found.')
            continue
        for idx, (s, e) in enumerate(windows, start=1):
            path = save_window(df, pattern_type, idx, s, e)
            print('  [%d] rows %d-%d  (%d bars)  saved: %s' % (
                idx, s, e, e - s, os.path.basename(path)))
        print('  Saved %d example(s).' % len(windows))
        total_saved += len(windows)

    print('\n' + '=' * 50)
    print('Total pattern files saved: %d' % total_saved)
    print('Patterns directory: %s' % os.path.abspath(PATTERNS_PATH))


if __name__ == '__main__':
    main()
