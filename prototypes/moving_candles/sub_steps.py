"""Split one finished candle into steps, so it can be shown forming over time.

The data only has the final Open/High/Low/Close of each candle, nothing about
what happened inside it. So we invent a believable price path inside the candle:

    up candle   (Close >= Open):  Open -> Low  -> High -> Close
    down candle (Close <  Open):  Open -> High -> Low  -> Close

with a little random noise. The path always touches the real High and Low and
ends on the real Close, so once the last step is shown the candle is EXACTLY the
one in the file. The noise is seeded, so the same candle always plays the same way.

Example with 4 steps (a 1 h candle updated at 15, 30, 45 min, then closed):
    step 1: open=O, high/low = extremes so far, close = price at 15 min
    ...
    step 4: open=O, high=H, low=L, close=C   (the real candle)
"""
import numpy as np

TICKS_PER_STEP = 15  # points of the invented path per step (like minutes)


def price_path(o, h, l, c, n_steps=4, seed=0):
    """Invented price path inside the candle: n_steps * TICKS_PER_STEP + 1 points."""
    n = n_steps * TICKS_PER_STEP
    rng = np.random.default_rng(seed)

    if h == l:  # flat candle, nothing moves
        return np.full(n + 1, o)

    first, second = (l, h) if c >= o else (h, l)
    # When the two extremes are reached (as a share of the candle's time)
    t1 = rng.uniform(0.15, 0.45)
    t2 = rng.uniform(t1 + 0.15, 0.85)
    i1, i2 = round(t1 * n), round(t2 * n)

    path = np.concatenate([
        np.linspace(o, first, i1 + 1)[:-1],
        np.linspace(first, second, i2 - i1 + 1)[:-1],
        np.linspace(second, c, n - i2 + 1),
    ])

    # Wiggle the in-between points, but stay inside the real High/Low
    noise = rng.normal(0, (h - l) * 0.04, n + 1)
    path = np.clip(path + noise, l, h)
    # Pin the points that must be exact
    path[0], path[i1], path[i2], path[-1] = o, first, second, c
    return path


def split_candle(o, h, l, c, n_steps=4, seed=0):
    """List of n_steps partial candles (open, high, low, close); the last one is the real candle."""
    path = price_path(o, h, l, c, n_steps, seed)
    steps = []
    for k in range(1, n_steps + 1):
        seen = path[: k * TICKS_PER_STEP + 1]
        steps.append((o, float(seen.max()), float(seen.min()), float(seen[-1])))
    steps[-1] = (o, h, l, c)  # exact, no rounding drift
    return steps


if __name__ == "__main__":
    # Quick self-check: the last step must always equal the real candle,
    # and every step must stay inside the real High/Low.
    rng = np.random.default_rng(1)
    for i in range(10_000):
        o, c = rng.uniform(90, 110, 2)
        h = max(o, c) + rng.uniform(0, 5)
        l = min(o, c) - rng.uniform(0, 5)
        n = int(rng.integers(2, 13))
        steps = split_candle(o, h, l, c, n, seed=i)
        assert steps[-1] == (o, h, l, c)
        for so, sh, sl, sc in steps:
            assert l <= sl <= min(so, sc) and max(so, sc) <= sh <= h
    print("OK: 10,000 random candles, last step always equals the real candle")
    print("Example (O=100, H=105, L=98, C=103, 4 steps):")
    for k, s in enumerate(split_candle(100, 105, 98, 103, 4, seed=7), 1):
        print(f"  step {k}: open={s[0]:.2f} high={s[1]:.2f} low={s[2]:.2f} close={s[3]:.2f}")
