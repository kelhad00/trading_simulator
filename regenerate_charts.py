"""
Regenerate synthetic chart data for all companies missing from generated_data.csv.

Run from the trading_simulator directory inside the project venv:
    python regenerate_charts.py

Uses the same parameters as the Settings → Charts modal defaults:
    alpha=500, length=100, start_value=250, 2 segments per company.
"""

import os
import sys
import random
import numpy as np
import pandas as pd

# ── Path setup ─────────────────────────────────────────────────────────────────
# Allow imports from the trade package without the full Dash app running
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

DATA_PATH = os.path.join(script_dir, "Data")
CAC40_PATH = os.path.join(DATA_PATH, "CAC40.csv")
OUT_PATH = os.path.join(DATA_PATH, "generated_data.csv")
START_DATE = "2021-01-01"
START_VALUE = 250.0
ALPHA = 500
LENGTH = 100
N_SEGMENTS = 3

COMPANIES = {
    "MC.PA":    "LVMH MOËT HENNESSY LOUIS VUITTON SE (MC)",
    "OR.PA":    "L'ORÉAL (OR)",
    "RMS.PA":   "HERMÈS INTERNATIONAL (RMS)",
    "TTE.PA":   "TOTALENERGIES SE (TTE)",
    "SAN.PA":   "SANOFI (SAN)",
    "AIR.PA":   "AIRBUS SE (AIR)",
    "SU.PA":    "SCHNEIDER ELECTRIC SE (SU)",
    "AI.PA":    "AIR LIQUIDE (AI)",
    "EL.PA":    "ESSILORLUXOTTICA (EL)",
    "BNP.PA":   "BNP PARIBAS (BNP)",
    "KER.PA":   "KERING (KER)",
    "DG.PA":    "VINCI (DG)",
    "CS.PA":    "AXA (CS)",
    "SAF.PA":   "SAFRAN (SAF)",
    "RI.PA":    "PERNOD RICARD (RI)",
    "DSY.PA":   "DASSAULT SYSTÈMES SE (DSY)",
    "STLAM.MI": "STELLANTIS N.V. (STLAM)",
    "BN.PA":    "DANONE (BN)",
    "STMPA.PA": "STMICROELECTRONICS N.V. (STMPA)",
    "ACA.PA":   "CRÉDIT AGRICOLE S.A. (ACA)",
    "^GSPC":    "S&P 500",
    "^DJI":     "Dow Jones Industrial Average",
    "^FCHI":    "CAC 40",
    "^SPGSGC":  "S&P GSCI Gold Index",
}


# ── Helpers (mirrors create_market_data.py) ────────────────────────────────────

def load_data(path):
    return pd.read_csv(path).dropna()


def scale_market_data(df, previous_close):
    scale_factor = previous_close / df.at[0, "Open"]
    out = df.copy()
    out[["Open", "High", "Low", "Close"]] *= scale_factor
    return out


def bull_trend(data, data_size, alpha=500, length=100):
    for _ in range(2000):
        r = random.randint(1, data_size - length - 1)
        if (data["Close"].iloc[r] < data["Close"].iloc[r + length] and
                data["Close"].iloc[r + length] - data["Close"].iloc[r] >= alpha):
            return r
    raise RuntimeError("No bull trend found after 2000 tries")


def bear_trend(data, data_size, alpha=500, length=100):
    for _ in range(2000):
        r = random.randint(1, data_size - length - 1)
        if (data["Close"].iloc[r] > data["Close"].iloc[r + length] and
                data["Close"].iloc[r] - data["Close"].iloc[r + length] >= alpha):
            return r
    raise RuntimeError("No bear trend found after 2000 tries")


def flat_trend(data, data_size, alpha=50, length=100):
    for _ in range(2000):
        r = random.randint(1, data_size - length - 1)
        std = np.std(data["Close"].iloc[r: r + length])
        if abs(data["Close"].iloc[r] - data["Close"].iloc[r + length]) <= alpha and std <= 80:
            return r
    raise RuntimeError("No flat trend found after 2000 tries")


def pick_random_trend(data, data_size, alpha, length):
    choice = random.choice(["bull", "bear", "flat"])
    if choice == "bull":
        return bull_trend(data, data_size, alpha, length)
    elif choice == "bear":
        return bear_trend(data, data_size, alpha, length)
    else:
        return flat_trend(data, data_size, 20, length)


def format_and_combine(raw_df, stock, first_timestamp):
    df = raw_df.copy()
    df["Date"] = pd.date_range(start=first_timestamp, periods=len(df), freq="D")
    df.set_index("Date", inplace=True)
    df.index.name = "date"
    df.index = pd.to_datetime(df.index, utc=True).tz_convert("Europe/Paris")

    df["long_MA"]  = df["Close"].rolling(window=20,  min_periods=1).mean()
    df["short_MA"] = df["Close"].rolling(window=50,  min_periods=1).mean()
    df["200_MA"]   = df["Close"].rolling(window=200, min_periods=1).mean()
    df.rename(columns={"Adj Close": "adjclose"}, inplace=True)

    columns = pd.MultiIndex.from_tuples(
        [(stock, col) for col in df.columns], names=["symbol", None]
    )
    out = pd.DataFrame(index=df.index, columns=columns)
    for col in df.columns:
        out[(stock, col)] = df[col].values
    return out


def get_existing_data():
    try:
        df = pd.read_csv(OUT_PATH, index_col=0, header=[0, 1])
        if df.empty or len(df.columns) == 0:
            return None
        return df
    except Exception:
        return None


def save_data(df):
    df.to_csv(OUT_PATH, index=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"Loading CAC40 dataset from {CAC40_PATH}...")
    dataset = load_data(CAC40_PATH)
    data_size = len(dataset)
    print(f"  Dataset size: {data_size} rows")

    existing = get_existing_data()
    already_done = set()
    if existing is not None:
        already_done = set(existing.columns.get_level_values("symbol").unique())
        print(f"Companies already in generated_data.csv: {sorted(already_done)}")
    else:
        print("generated_data.csv is empty — regenerating all companies.")

    missing = [s for s in COMPANIES if s not in already_done]
    if not missing:
        print("All companies already have chart data. Nothing to do.")
        return

    print(f"\nRegenerating {len(missing)} companies: {missing}\n")

    combined = existing

    for stock in missing:
        print(f"  [{stock}] Generating {N_SEGMENTS} segments (alpha={ALPHA}, length={LENGTH})...", end=" ", flush=True)
        try:
            segments = []
            prev_close = START_VALUE
            for _ in range(N_SEGMENTS):
                idx = pick_random_trend(dataset, data_size, ALPHA, LENGTH)
                seg = dataset[idx: idx + LENGTH].reset_index(drop=True)
                seg = scale_market_data(seg, prev_close)
                segments.append(seg)
                prev_close = float(seg.iloc[-1]["Close"])

            raw = pd.concat(segments).reset_index(drop=True)
            formatted = format_and_combine(raw, stock, START_DATE)

            if combined is not None:
                combined.index = pd.to_datetime(combined.index, utc=True).tz_convert("Europe/Paris")
                combined = pd.concat([combined, formatted], axis=1)
            else:
                combined = formatted

            print("OK")
        except Exception as e:
            print(f"FAILED ({e})")

    if combined is not None:
        save_data(combined)
        print(f"\nSaved to {OUT_PATH}")
    else:
        print("\nNothing was generated.")


if __name__ == "__main__":
    main()
