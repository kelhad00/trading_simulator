En cours d'écriture....

# TradeSim
TradeSim is a web application that allows users to simulate trading stocks, and other financial instruments. 
The application is built using Dash.
Reasearchers can use this application to simulate trading strategies and export datas to analyze the results.

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

## Run the tests
Automated checks for moving candles, orders, news tags, settings, translations, session files and
the data folder. They use a small invented dataset in a temporary folder, so they never touch real
data and work on any computer.

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
### Files
- `app_config.py` / `app_runtime.py` : start the configurator (port 8050) / runtime (port 8051) version
- `app.py` : defines the application and contains the stores (not run directly)
- `callbacks` : folder containing all the callbacks (dynamic functions, user interactions)
- `components` : folder containing all the static & reusable front-end elements
- `layouts` : folder containing all the layouts of the application
- `assets` : folder containing all the static files (css, images, etc.)
- `locales` : folder containing all the translations for each language
- `pages` : folder containing all the pages of the application. **import the layouts and specific callbacks files.**
- `utils` : folder containing all the static & utility functions
- `defaults.py` : file containing all the default values for the application

### Styling
- `Tailwind CSS` is used for the styling of the application. (https://tailwindcss.com/)
- `Dash Mantine Components` is used for the visual components. (version 1.12) (https://dmc-docs-0-12.onrender.com/)

### Callbacks
Each callback is sorted by the page it is used in.
Actually there is 2 main pages :
- `dashboard` 
- `settings` 
#### Dashboard
Dashboard is divided in 5 main sections :
- `portfolio` : all the callbacks related to the portfolio (updated by requests too)
- `graph` : all the callbacks related to the graph (market_data and revenue)
- `news` : all the callbacks related to the news
- `request` : all the callbacks related to the requests (update the portfolio too)
- `export` : all the callbacks related to the export of the data
#### Settings
Settings is divided in 6 sections :
- `charts` : all the callbacks related to the charts and their generation
- `news` : all the callbacks related to the generation of the news
- `revenues` : all the callbacks related to the revenues and their generation
- `stocks` : all the callbacks related to the tickers
- `advanced` : all the callbacks related to the advanced settings
- `upload` : all the callbacks related to the upload of the data

## Why was this project created?
In the financial laboratories of the University of Mons, a study has been launched to analyse the reactions of traders to the stock markets. 
To better understand which factors are most important in their choices, what is the "human" part of this equation, and many other questions. 
To improve their results, the researchers needed to create a controlled, automated data-gathering environment. 
tradesim is an independent part of this environment, to which several sensors have been added. 
To find out more, have a look at the corresponding repository here.

## Contributing
Feel free to create an issue/PR if you want to see anything else implemented.

## Legal Stuff
tradesim is distributed under the Apache License 2.0. See the LICENSE file in the release for details.


