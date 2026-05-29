"""
validate_patterns.py
====================
Validates each pattern CSV in data/patterns/ using independent geometric checks
(distinct from detect_patterns.py's sliding-window algorithm), computes a
quality score per file, and writes data/patterns/quality_scores.json.

Writes a console report showing per-type false-positive rate and average score.

Run from the trading_simulator/trade/ directory:
    python utils/settings/validate_patterns.py
"""

import os
import glob
import json
from itertools import combinations

import numpy as np
import pandas as pd

DATA_PATH     = '../data'
PATTERNS_PATH = os.path.join(DATA_PATH, 'patterns')
OUTPUT_FILE   = os.path.join(PATTERNS_PATH, 'quality_scores.json')
SMOOTH_W      = 5


# ── Shared helpers ────────────────────────────────────────────────────────────

def smooth(arr, w=SMOOTH_W):
    return pd.Series(arr).rolling(w, center=True, min_periods=1).mean().values


def find_peaks(arr, min_dist=5):
    """Local maxima with minimum bar separation."""
    out = []
    for i in range(1, len(arr) - 1):
        if arr[i] >= arr[i - 1] and arr[i] >= arr[i + 1]:
            if not out or i - out[-1] >= min_dist:
                out.append(i)
            elif arr[i] > arr[out[-1]]:
                out[-1] = i
    return out


def find_troughs(arr, min_dist=5):
    """Local minima with minimum bar separation."""
    out = []
    for i in range(1, len(arr) - 1):
        if arr[i] <= arr[i - 1] and arr[i] <= arr[i + 1]:
            if not out or i - out[-1] >= min_dist:
                out.append(i)
            elif arr[i] < arr[out[-1]]:
                out[-1] = i
    return out


def linreg_slope(x, y):
    """Raw (unnormalized) linear regression slope."""
    x = np.array(x, float)
    y = np.array(y, float)
    x -= x.mean()
    return float(np.dot(x, y) / (np.dot(x, x) + 1e-12))


# ── Quality sub-scores ────────────────────────────────────────────────────────

def snr_score(closes):
    """Signal-to-noise: total swing divided by mean daily move, scaled to 0-100."""
    swing = closes.max() - closes.min()
    noise = np.abs(np.diff(closes)).mean() + 1e-8
    return int(min(swing / noise / 15.0, 1.0) * 100)


def symmetry_score(sp, pattern_type):
    """
    Bilateral symmetry 0-100 for symmetric pattern types.
    Returns 75 (neutral) for directional patterns.
    """
    if pattern_type == 'head_and_shoulders':
        _peaks = find_peaks(sp, min_dist=5)
        for i, j, k in combinations(range(len(_peaks)), 3):
            p1, p2, p3 = _peaks[i], _peaks[j], _peaks[k]
            h1, h2, h3 = sp[p1], sp[p2], sp[p3]
            if h2 > h1 and h2 > h3:
                return int(max(0.0, 1.0 - abs(h1 - h3) / (h2 + 1e-8)) * 100)
        return 50

    if pattern_type == 'inverse_head_and_shoulders':
        _troughs = find_troughs(sp, min_dist=5)
        for i, j, k in combinations(range(len(_troughs)), 3):
            t1, t2, t3 = _troughs[i], _troughs[j], _troughs[k]
            h1, h2, h3 = sp[t1], sp[t2], sp[t3]
            if h2 < h1 and h2 < h3:
                return int(max(0.0, 1.0 - abs(h1 - h3) / (min(h1, h3) + 1e-8)) * 100)
        return 50

    if pattern_type == 'double_top':
        peaks = find_peaks(sp, min_dist=4)
        best = 0.0
        for i in range(len(peaks) - 1):
            for j in range(i + 1, len(peaks)):
                h1, h2 = sp[peaks[i]], sp[peaks[j]]
                best = max(best, 1.0 - abs(h1 - h2) / (max(h1, h2) + 1e-8))
        return int(best * 100)

    if pattern_type == 'double_bottom':
        troughs = find_troughs(sp, min_dist=4)
        best = 0.0
        for i in range(len(troughs) - 1):
            for j in range(i + 1, len(troughs)):
                h1, h2 = sp[troughs[i]], sp[troughs[j]]
                best = max(best, 1.0 - abs(h1 - h2) / (min(h1, h2) + 1e-8))
        return int(best * 100)

    return 75   # neutral for directional patterns


# ── Per-pattern validators ────────────────────────────────────────────────────
# Each returns (valid: bool, reason: str, conformity: float 0-100)

def val_head_and_shoulders(closes, sp):
    peaks = find_peaks(sp, min_dist=5)
    if len(peaks) < 3:
        return False, 'fewer than 3 peaks found', 0.0
    # Check all ordered triplets, not just consecutive ones
    for i, j, k in combinations(range(len(peaks)), 3):
        p1, p2, p3 = peaks[i], peaks[j], peaks[k]
        h1, h2, h3 = sp[p1], sp[p2], sp[p3]
        if not (h2 > h1 and h2 > h3):
            continue
        shoulder_diff = abs(h1 - h3) / (h2 + 1e-8)
        if shoulder_diff > 0.15:
            continue
        prominence = (h2 - max(h1, h3)) / (h2 + 1e-8)
        if prominence < 0.02:
            continue
        # Independent check: neckline trough must be at least 1% below the lower shoulder
        trough_between = sp[p1:p3].min()
        if trough_between > min(h1, h3) * 0.99:
            return False, 'neckline trough too shallow (< 1%% below lower shoulder)', 0.0
        return True, '', min(prominence / 0.08, 1.0) * 100
    return False, 'no valid H&S triplet (middle peak not tallest or shoulders asymmetric)', 0.0


def val_inverse_head_and_shoulders(closes, sp):
    troughs = find_troughs(sp, min_dist=5)
    if len(troughs) < 3:
        return False, 'fewer than 3 troughs found', 0.0
    # Check all ordered triplets, not just consecutive ones
    for i, j, k in combinations(range(len(troughs)), 3):
        t1, t2, t3 = troughs[i], troughs[j], troughs[k]
        h1, h2, h3 = sp[t1], sp[t2], sp[t3]
        if not (h2 < h1 and h2 < h3):
            continue
        shoulder_diff = abs(h1 - h3) / (min(h1, h3) + 1e-8)
        if shoulder_diff > 0.15:
            continue
        prominence = (min(h1, h3) - h2) / (min(h1, h3) + 1e-8)
        if prominence < 0.02:
            continue
        # Independent check: neckline (peaks between t1-t2 and t2-t3) is roughly horizontal
        nl_left  = sp[t1:t2].max() if t2 > t1 else sp[t1]
        nl_right = sp[t2:t3].max() if t3 > t2 else sp[t2]
        nl_tilt  = abs(nl_left - nl_right) / (max(nl_left, nl_right) + 1e-8)
        if nl_tilt > 0.15:
            return False, 'neckline too tilted (%.1f%% difference between left and right peaks)' % (nl_tilt * 100), 0.0
        return True, '', min(prominence / 0.08, 1.0) * 100
    return False, 'no valid inv-H&S triplet (middle trough not deepest or shoulders asymmetric)', 0.0


def val_double_top(closes, sp):
    peaks = find_peaks(sp, min_dist=4)
    if len(peaks) < 2:
        return False, 'fewer than 2 peaks found', 0.0
    best = None
    for i in range(len(peaks) - 1):
        for j in range(i + 1, len(peaks)):
            p1, p2 = peaks[i], peaks[j]
            h1, h2 = sp[p1], sp[p2]
            diff = abs(h1 - h2) / (max(h1, h2) + 1e-8)
            if diff > 0.03:
                continue
            trough_val  = sp[p1:p2].min()
            trough_depth = (max(h1, h2) - trough_val) / (max(h1, h2) + 1e-8)
            if trough_depth < 0.03:
                continue
            if best is None or diff < best[0]:
                best = (diff, trough_depth)
    if best is None:
        return False, 'no two peaks within 3% with a clear trough (>=3%) between them', 0.0
    _, trough_depth = best
    return True, '', min(trough_depth / 0.08, 1.0) * 100


def val_double_bottom(closes, sp):
    troughs = find_troughs(sp, min_dist=4)
    if len(troughs) < 2:
        return False, 'fewer than 2 troughs found', 0.0
    best = None
    for i in range(len(troughs) - 1):
        for j in range(i + 1, len(troughs)):
            t1, t2 = troughs[i], troughs[j]
            h1, h2 = sp[t1], sp[t2]
            diff = abs(h1 - h2) / (min(h1, h2) + 1e-8)
            if diff > 0.03:
                continue
            peak_val    = sp[t1:t2].max()
            peak_height = (peak_val - min(h1, h2)) / (min(h1, h2) + 1e-8)
            if peak_height < 0.03:
                continue
            if best is None or diff < best[0]:
                best = (diff, peak_height)
    if best is None:
        return False, 'no two troughs within 3% with a clear peak (>=3%) between them', 0.0
    _, peak_height = best
    return True, '', min(peak_height / 0.08, 1.0) * 100


def val_ascending_triangle(closes, sp):
    peaks   = find_peaks(sp,   min_dist=4)
    troughs = find_troughs(sp, min_dist=4)
    if len(peaks) < 2 or len(troughs) < 2:
        return False, 'insufficient peaks or troughs', 0.0
    ph = [sp[p] for p in peaks]
    th = [sp[t] for t in troughs]
    # Resistance: peaks flat within 5%
    res_range = (max(ph) - min(ph)) / (max(ph) + 1e-8)
    if res_range > 0.05:
        return False, 'resistance not flat (peaks vary %.1f%%)' % (res_range * 100), 0.0
    # Support: troughs rising by regression (independent from detect_patterns.py's strict monotone check)
    sup_slope = linreg_slope(list(range(len(troughs))), th)
    if sup_slope <= 0:
        return False, 'support not rising (trough regression slope <= 0)', 0.0
    res_slope = abs(linreg_slope(list(range(len(peaks))), ph))
    if res_slope > sup_slope * 0.40:
        return False, 'resistance not sufficiently flat relative to rising support', 0.0
    return True, '', min(sup_slope / (sup_slope + res_slope + 1e-8), 1.0) * 100


def val_descending_triangle(closes, sp):
    peaks   = find_peaks(sp,   min_dist=4)
    troughs = find_troughs(sp, min_dist=4)
    if len(peaks) < 2 or len(troughs) < 2:
        return False, 'insufficient peaks or troughs', 0.0
    ph = [sp[p] for p in peaks]
    th = [sp[t] for t in troughs]
    # Support: troughs flat within 5%
    sup_range = (max(th) - min(th)) / (max(th) + 1e-8)
    if sup_range > 0.05:
        return False, 'support not flat (troughs vary %.1f%%)' % (sup_range * 100), 0.0
    # Resistance: peaks falling by regression
    res_slope = linreg_slope(list(range(len(peaks))), ph)
    if res_slope >= 0:
        return False, 'resistance not falling (peak regression slope >= 0)', 0.0
    sup_slope = abs(linreg_slope(list(range(len(troughs))), th))
    if sup_slope > abs(res_slope) * 0.40:
        return False, 'support not flat relative to falling resistance', 0.0
    return True, '', min(abs(res_slope) / (abs(res_slope) + sup_slope + 1e-8), 1.0) * 100


def val_bullish_flag(closes, sp):
    n        = len(sp)
    pole_end = max(3, n // 3)
    pole     = sp[:pole_end]
    flag     = sp[pole_end:]
    if len(flag) < 5:
        return False, 'flag section too short', 0.0
    pole_return = (pole[-1] - pole[0]) / (pole[0] + 1e-8)
    if pole_return < 0.03:
        return False, 'pole return too weak (%.1f%% < 3%%)' % (pole_return * 100), 0.0
    pole_move  = pole[-1] - pole[0]
    flag_range = max(flag) - min(flag)
    if flag_range > 0.50 * pole_move:
        return False, 'flag consolidation too wide (> 50%% of pole)', 0.0
    # Independent: flag slope must not be upward (would negate the consolidation)
    flag_slope = linreg_slope(range(len(flag)), flag)
    if flag_slope > pole_move * 0.01:
        return False, 'flag is rising instead of consolidating', 0.0
    return True, '', min(pole_return / 0.10, 1.0) * 100


def val_bearish_flag(closes, sp):
    n        = len(sp)
    pole_end = max(3, n // 3)
    pole     = sp[:pole_end]
    flag     = sp[pole_end:]
    if len(flag) < 5:
        return False, 'flag section too short', 0.0
    pole_return = (pole[0] - pole[-1]) / (pole[0] + 1e-8)
    if pole_return < 0.03:
        return False, 'pole drop too weak (%.1f%% < 3%%)' % (pole_return * 100), 0.0
    pole_move  = pole[0] - pole[-1]
    flag_range = max(flag) - min(flag)
    if flag_range > 0.55 * pole_move:
        return False, 'flag consolidation too wide (> 55%% of pole)', 0.0
    flag_slope = linreg_slope(range(len(flag)), flag)
    if flag_slope < -pole_move * 0.01:
        return False, 'flag is falling instead of consolidating', 0.0
    return True, '', min(pole_return / 0.08, 1.0) * 100


def val_cup_and_handle(closes, sp):
    n     = len(sp)
    rim_w = max(4, n // 7)
    left_rim  = float(np.mean(sp[:rim_w]))
    right_rim = float(np.mean(sp[n - rim_w * 2: n - rim_w]))
    handle    = sp[n - rim_w:]
    cup_body  = sp[rim_w: n - rim_w * 2]
    if len(cup_body) < 6:
        return False, 'cup body too short', 0.0
    cup_min  = float(min(cup_body))
    rim_diff = abs(left_rim - right_rim) / (left_rim + 1e-8)
    if rim_diff > 0.10:
        return False, 'rims not equal (%.1f%% difference)' % (rim_diff * 100), 0.0
    depth = (left_rim - cup_min) / (left_rim + 1e-8)
    if not (0.05 < depth < 0.40):
        return False, 'cup depth out of range (%.1f%%)' % (depth * 100), 0.0
    handle_range = max(handle) - min(handle)
    if handle_range > 0.5 * depth * left_rim:
        return False, 'handle pullback too large', 0.0
    # Independent: cup bottom must sit in the middle half of the full pattern
    bottom_idx = int(np.argmin(sp[rim_w: n - rim_w * 2])) + rim_w
    if not (n // 4 <= bottom_idx <= 3 * n // 4):
        return False, 'cup bottom not centered in the pattern', 0.0
    return True, '', min(depth / 0.20, 1.0) * 100


def val_rising_wedge(closes, sp):
    peaks   = find_peaks(sp,   min_dist=4)
    troughs = find_troughs(sp, min_dist=4)
    if len(peaks) < 2 or len(troughs) < 2:
        return False, 'insufficient peaks or troughs', 0.0
    ph = [sp[p] for p in peaks]
    th = [sp[t] for t in troughs]
    sl_p = linreg_slope(list(range(len(peaks))),   ph)
    sl_t = linreg_slope(list(range(len(troughs))), th)
    if sl_p <= 0:
        return False, 'peaks not rising', 0.0
    if sl_t <= 0:
        return False, 'troughs not rising', 0.0
    if sl_t <= sl_p * 1.05:
        return False, 'support not rising faster than resistance (lines not converging)', 0.0
    # Independent: price range narrowing from first half to second half
    mid = len(sp) // 2
    r_first  = max(sp[:mid]) - min(sp[:mid])
    r_second = max(sp[mid:]) - min(sp[mid:])
    if r_second >= r_first * 0.95:
        return False, 'price range not narrowing (no convergence)', 0.0
    return True, '', min((sl_t - sl_p) / (sl_p + 1e-8), 1.0) * 100


def val_falling_wedge(closes, sp):
    peaks   = find_peaks(sp,   min_dist=4)
    troughs = find_troughs(sp, min_dist=4)
    if len(peaks) < 2 or len(troughs) < 2:
        return False, 'insufficient peaks or troughs', 0.0
    ph = [sp[p] for p in peaks]
    th = [sp[t] for t in troughs]
    sl_p = linreg_slope(list(range(len(peaks))),   ph)
    sl_t = linreg_slope(list(range(len(troughs))), th)
    if sl_p >= 0:
        return False, 'peaks not falling', 0.0
    if sl_t >= 0:
        return False, 'troughs not falling', 0.0
    if sl_p >= sl_t * 1.05:
        return False, 'resistance not falling faster than support (lines not converging)', 0.0
    mid = len(sp) // 2
    r_first  = max(sp[:mid]) - min(sp[:mid])
    r_second = max(sp[mid:]) - min(sp[mid:])
    if r_second >= r_first * 0.95:
        return False, 'price range not narrowing (no convergence)', 0.0
    return True, '', min((sl_t - sl_p) / (abs(sl_t) + 1e-8), 1.0) * 100


VALIDATORS = {
    'head_and_shoulders':         val_head_and_shoulders,
    'inverse_head_and_shoulders': val_inverse_head_and_shoulders,
    'double_top':                 val_double_top,
    'double_bottom':              val_double_bottom,
    'ascending_triangle':         val_ascending_triangle,
    'descending_triangle':        val_descending_triangle,
    'bullish_flag':               val_bullish_flag,
    'bearish_flag':               val_bearish_flag,
    'cup_and_handle':             val_cup_and_handle,
    'rising_wedge':               val_rising_wedge,
    'falling_wedge':              val_falling_wedge,
}


# ── Report ────────────────────────────────────────────────────────────────────

def print_report(results):
    print('\n' + '=' * 65)
    print('PATTERN VALIDATION REPORT')
    print('=' * 65)

    total = 0
    invalid_total = 0
    type_stats = []

    for pt, files in results.items():
        n       = len(files)
        n_inv   = sum(1 for f in files.values() if not f['valid'])
        avg_sc  = sum(f['score'] for f in files.values()) / max(n, 1)
        err_pct = n_inv / max(n, 1) * 100
        type_stats.append((pt, n, n_inv, err_pct, avg_sc))
        total        += n
        invalid_total += n_inv

    type_stats.sort(key=lambda x: x[3], reverse=True)

    print('\n%-36s %5s %7s %6s %9s' % ('Pattern Type', 'Files', 'Invalid', 'Err%', 'AvgScore'))
    print('-' * 67)
    for pt, n, n_inv, err, avg in type_stats:
        print('%-36s %5d %7d %5.0f%% %9.0f' % (pt, n, n_inv, err, avg))

    print('-' * 67)
    overall = invalid_total / max(total, 1) * 100
    print('OVERALL: %d files, %d invalid, error rate = %.0f%%' % (total, invalid_total, overall))

    if invalid_total:
        print('\nFailed patterns:')
        for pt, files in results.items():
            for fname, info in files.items():
                if not info['valid']:
                    print('  %s/%s: %s' % (pt, fname, info['reason']))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    results = {}

    for folder in sorted(glob.glob(PATTERNS_PATH + '/*/')):
        pattern_type = os.path.basename(folder.rstrip('/\\'))
        validator = VALIDATORS.get(pattern_type)
        if validator is None:
            print('[SKIP] %s — no validator defined' % pattern_type)
            continue

        results[pattern_type] = {}
        files = sorted(glob.glob(os.path.join(folder, '*.csv')))
        print('Validating %-35s (%d files)' % (pattern_type, len(files)))

        for fpath in files:
            fname  = os.path.basename(fpath)
            df     = pd.read_csv(fpath).dropna().reset_index(drop=True)
            closes = df['Close'].values
            sp     = smooth(closes)

            valid, reason, conformity = validator(closes, sp)
            snr  = snr_score(closes)
            sym  = symmetry_score(sp, pattern_type)
            conf = int(conformity)
            score = int((snr + sym + conf) / 3)

            results[pattern_type][fname] = {
                'valid':  valid,
                'score':  score,
                'reason': reason,
            }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print('\nWritten: %s' % os.path.abspath(OUTPUT_FILE))

    print_report(results)


if __name__ == '__main__':
    main()
