# Moving candles prototype

Standalone test of **TradingView-style forming candles**: instead of appearing fully formed, each candle
updates step by step. For example, a 1 h candle updates at 15, 30 and 45 min and then closes.

It loads the same `session.zip` that TradeSim exports, but it is fully separate from the simulator:

- it doesn't import or change anything in `trade/`;
- it reads `session.zip` **in memory** and never writes to `Data/`;
- it runs on port **8052**, so TradeSim (8050) can run at the same time.

## Run

From the `trading_simulator` folder:

```powershell
.\trade\venv\Scripts\Activate.ps1
python prototypes\moving_candles\app.py --zip "C:\Users\MrEugeene\Downloads\session (8).zip"
```

Open http://127.0.0.1:8052. You can also start without `--zip` and drop a `session.zip` on the page.

Controls: company, steps per candle (4 = 15/30/45/60 min), speed, how many candles are already shown at the
start, **Play/Pause**, **Next step** (one step at a time) and **Reset**.

The forming candle is drawn in blue/orange. The info box shows its current values, and when it closes it shows
the real candle from the file with a ✔ if they match.

Self-check of the candle-splitting logic:

```powershell
cd prototypes\moving_candles
python sub_steps.py
```

## How it works

The data only has the **final** Open/High/Low/Close of each candle (one per day in `generated_data.csv`).
Nothing is known about what happened inside a candle, so `sub_steps.py` invents a believable path inside it:

- up candle: Open → Low → High → Close
- down candle: Open → High → Low → Close

It adds a little random noise, but always stays inside the real High/Low. After step *k* the candle shows:
open = real Open, high/low = the extremes reached so far, close = the current price. The **last step is exactly
the real candle**. This was checked on 10,000 random candles and on every candle of all 49 tickers in the
test session. The noise is seeded per company and candle, so the same candle always plays the same way.

| File | Role |
|---|---|
| `load_session.py` | Reads `session.zip` (settings + `generated_data.csv`) in memory |
| `sub_steps.py` | Splits one candle into N growing steps |
| `app.py` | Dash page that plays the candles |

## What TradeSim would need to change

Notes for deciding how to bring this into the simulator:

1. **Order execution:** orders are currently checked against a whole candle's High/Low. With forming candles,
   an order should fill only when the **current** price (or the range so far) reaches it. Otherwise a trader
   could get filled at a price the chart hasn't shown yet.
2. **Timing and config:** `update_time` currently means "one new candle per tick". It would become "one step
   per tick", so a session needs N times more ticks, or a shorter update time. It needs a new setting for
   steps per candle, and `simulation-duration` would have to be recomputed.
3. **Data generator:** either keep generating daily OHLC and split candles at play time (as here, with no
   file-format change), or generate and store the in-between prices so every participant sees exactly the
   same path. The second option is better for research reproducibility, but it changes `generated_data.csv`.
4. **Chart:** the dashboard chart (`trade/utils/graph/candlestick_charts.py`) would redraw the last candle
   each step. The fixed-slot layout already fits this, because the forming candle stays in its slot.
5. **News:** news is placed by date/candle. It needs to decide at which step inside a candle a news item
   appears, e.g. at the open, or tied to a step so the price reacts after it.
6. **Logs/exports:** interface, portfolio and request logs should record the step as well as the candle, so
   researchers know what price the participant saw when acting.
7. **Portfolio/P&L:** values would update every step from the current price, not only at the close.
