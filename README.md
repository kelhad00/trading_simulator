# TradeSim
TradeSim is a web application that simulates trading stocks and indexes, built with Dash.
Researchers prepare a market (prices, news, company revenue) and run sessions with participants;
every action of the participant is logged for analysis.

## Install required packages
Run the following command in the root folder:
```bash
pip install -r requirements.txt
```

## Start the app
Start the app from inside the `trade` folder, as shown below. The app always uses the data folder
`trading_simulator/data` (set in `trade/defaults.py`), whatever folder it is started from.

There are two versions:

| Version | For | Command (from the `trade` folder) | Open |
|---|---|---|---|
| Configurator | Researchers: settings, companies, charts, news | `python app_config.py` | http://127.0.0.1:8050 |
| Runtime | Running sessions with participants | `python app_runtime.py` | http://127.0.0.1:8051 |

```bash
cd trade
python app_config.py
```

With the virtual environment in `trade/venv` (Windows PowerShell):
```powershell
cd trade
.\venv\Scripts\python.exe app_config.py
```

Stop the app with `Ctrl + C`.

Notes:
- `python app.py` does **not** start the app: `app.py` only defines it.
- The configurator downloads market data at startup if `generated_data.csv` or `revenue.csv` is
  missing from the data folder.

## Running an experiment
1. **Prepare** the session in the Configurator (Settings page): companies, charts, news, revenues and
   the options below.
2. **Export** it with the **Export Session** button at the top of the Settings page: this gives
   `session.zip` (all settings + `generated_data.csv`, `news.csv`, `revenue.csv`).
3. On **each participant's computer**, start the Runtime and **import** `session.zip` on the home page;
   the Start button is enabled once a session is imported.
4. **Collect** the logs: each session writes to its own folder `data/exports/<session id>/`.

## Features
Every option is explained in the [WIKI](WIKI.md#settings-and-features) ([français](WIKI_FR.md#paramètres-et-fonctionnalités)).
The features added in 2026 are off until the researcher turns them on in the Settings.
- **Moving candles**: the newest candle forms in steps before it closes, like a live chart, with a
  Simple or Random price movement inside the candle.
- **Discrete mode (trials)**: the chart stops at chosen candles and the participant clicks "Next trial"
  (with a confirmation window, no news pop-ups, and a zoom on the first candles).
- **Leaderboard**: the participant against 20 robot traders made from the same prices.
- **Commission fee** on every executed buy and sell (0 by default).
- **News notifications**: on/off, filter by sentiment, show news some days early, sentiment tags on/off.
- **Time reminders** during the session (25 %, 50 %, 75 %, 5/2/1 minutes left).
- **Chart buttons** (on/off): Autoscale (fit the candles shown) and Reset axes (back to the live view).
- **Results window** at the end: final value and profit/loss, counting money put aside for waiting orders.
- **One log folder per session**, with the settings and code version (`log-info.json`).
- **"Updating…" screen** in the Configurator while it is working.
- **Works offline** (see below) and in **English and French** (`?lang=en` / `?lang=fr`).

For the next developer: [docs/HANDOVER.md](docs/HANDOVER.md) (state of the project, open issues,
decisions taken).

## Generating news
Generating news uses an AI (Ollama or Groq) to write the articles and a second model,
FinBERT, to check that each article really sounds positive or negative. FinBERT needs extra
packages (about 2 GB) that are only needed for generating news, not for running sessions.
Install them once in the same Python environment you start the app with:
```powershell
cd trade
.\venv\Scripts\python.exe -m pip install -r ..\requirements-news.txt
```
Without them the app still generates news, but **articles are not checked**: they are marked
`needs_review` in `verification_report.csv`, the terminal shows a NEWS CHECKER UNAVAILABLE
warning, and the pop-up after generation says how many articles were not checked.

## Working offline
Sessions work without internet: the page styling and the icons are files in `trade/assets/`
(`tailwind.css`, `icons.js`), not downloaded when a page opens. Only generating news (Groq, the
first FinBERT download) and downloading market data need internet.

If you add a new style class or icon to the code, rebuild the files (needs internet once).
The tests (`tests/test_offline.py`) say what is missing.
- Icons, from the `trading_simulator` folder:
  ```powershell
  .\trade\venv\Scripts\python.exe tools\fetch_icons.py
  ```
- Styling: download the Tailwind v3 standalone tool (`tailwindcss-windows-x64.exe`, from the
  Tailwind CSS releases on GitHub), then from the `trading_simulator` folder:
  ```powershell
  .\tailwindcss-windows-x64.exe -c tools\tailwind\tailwind.config.js -i tools\tailwind\input.css -o trade\assets\tailwind.css --minify
  ```

## Run the tests
About 300 automated checks (folder `tests/`) for moving candles, orders and money, fees, discrete
mode, the leaderboard, news, settings, translations, session files, logs and the data folder. They
use a small invented dataset in a temporary folder, so they never touch real data and work on any
computer.

Install the test tool once, then run all tests from the `trading_simulator` folder:
```powershell
.\trade\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\trade\venv\Scripts\python.exe -m pytest
```
Each dot is a passed check; a failure shows the test name and what went wrong. Run the tests
before committing a change.

## Requirements
- Python 3.10
- Packages in `requirements.txt`


## Structure
### Folders
| Path (in `trading_simulator`) | Contents |
|---|---|
| `trade/app_config.py` / `trade/app_runtime.py` | Start the Configurator (port 8050) / the Runtime (port 8051) |
| `trade/app.py` | Defines the application and all the stores (not run directly) |
| `trade/defaults.py` | Default values (money, timings, companies, data folder...) |
| `trade/pages/` | The three pages (home, settings, dashboard): import their layouts and callbacks |
| `trade/layouts/` | What each page shows |
| `trade/callbacks/` | What happens when the user does something (see below) |
| `trade/components/` | Reusable pieces of interface (header, menu, sections, sliders...) |
| `trade/utils/` | Logic without interface: candles, orders, fees, leaderboard, trials, logs, session file, news generation, market data |
| `trade/locales/` | Texts in English (`en.py`) and French (`fr.py`) |
| `trade/assets/` | Static files: local Tailwind CSS, icons, images |
| `data/` | Market data, news, revenue, and the session logs (`data/exports/`) |
| `tests/` | Automated tests (see "Run the tests") |
| `tools/` | Rebuild the local icons and Tailwind CSS (see "Working offline") |
| `docs/HANDOVER.md` | State of the project for the next developer |

### Callbacks
Sorted by the page they belong to.

**Home** (`trade/callbacks/`): `home.py` (Start and Export buttons), `home_import.py` (import a
session file), `reset.py` (Reset, end-of-session results).

**Dashboard** (`trade/callbacks/dashboard/`):
- `graph`: the chart, the clock, moving candles, pause, revenue chart
- `request`: placing, editing, cancelling and executing orders
- `portfolio`: cash, investment and the portfolio table
- `news`: the news list and the news pop-ups
- `reminders`: the time reminders
- `trials`: discrete mode ("Next trial" and its confirmation)
- `leaderboard`: the ranking against the robot traders
- `export`: the logs

**Settings** (`trade/callbacks/settings/`):
- `charts/`: generating market data (trends, patterns, events), then news in the background
- `news`: generating news
- `revenues`: company revenue
- `stocks`: the list of companies
- `advanced`: the Advanced tab (money, timings, fee, discrete mode, leaderboard...)
- `upload`: importing CSV files
- `session_export`: the Export Session button

### Styling
- [Tailwind CSS](https://tailwindcss.com/) for the layout (a local file, see "Working offline").
- [Dash Mantine Components 0.12](https://dmc-docs-0-12.onrender.com/) for the visual components.

## Why was this project created?
In the financial laboratories of the University of Mons, a study has been launched to analyse the reactions of traders to the stock markets.
To better understand which factors are most important in their choices, what is the "human" part of this equation, and many other questions.
To improve their results, the researchers needed to create a controlled, automated data-gathering environment.
TradeSim is an independent part of this environment, to which several sensors have been added.

## Contributing
Feel free to create an issue/PR if you want to see anything else implemented.

## Legal Stuff
tradesim is distributed under the Apache License 2.0. See the LICENSE file in the release for details.


