
## Wiki
- [Market](#market)
- [News](#news)
- [Revenues](#revenues)
- [Companies](#companies)
- [Settings and features](#settings-and-features)
- [Session file (session.zip)](#session-file-sessionzip)
- [Import](#import-)
- [Export](#export)


# Market
Market data can be configured for each ticker in the "Charts" section of the configuration page.

## Initialization
When you launch the application, market data will be scraped using yahooquery and yfinance.
These are real market data.

## Storage

### Path
Market data is stored in a CSV file.
Here is the file path: `data/generated_data.csv`

### Format
The data saved for each ticker are as follows:
- `Open`: The opening price
- `High`: The highest price
- `Low`: The lowest price
- `Close`: The closing price
- `Volume`: The volume of the day
- `adjclose`: The price adjusted for dividends and splits
- `long_MA`: The long-term moving average
- `short_MA`: The short-term moving average
- `200_MA`: The 200-day moving average

#### Index
- `date`: The date of the data

#### Columns
- `symbol`: The company's ticker
- `None`: The data columns (Open, High, Low, Close, Volume, adjclose, long_MA, short_MA, 200_MA)

#### Example
```csv
symbol,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,OR.PA,OR.PA,SAN.PA,SAN.PA,SAN.PA,^GSPC,^GSPC,^GSPC,^DJI,^DJI,^DJI,^FCHI,^FCHI,^FCHI,^SPGSGC,^SPGSGC,^SPGSGC
,Open,Open,Open,Open,Open,Open,High,High,High,High,High,High,Low,Low,Low,Low,Low,Low,Close,Close,Close,Close,Close,Close,Volume,Volume,Volume,Volume,Volume,Volume,adjclose,adjclose,adjclose,adjclose,adjclose,adjclose,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA
date,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2023-02-03 01:00:00+01:00,375.5,84.75,4136.68994140625,33926.30078125,7136.39990234375,0.0,384.3999938964844,86.33999633789062,4182.35986328125,34179.578125,7233.93994140625,0.0,373.8999938964844,82.25,4123.35986328125,33813.859375,7113.419921875,0.0,384.3999938964844,85.13999938964844,4136.47998046875,33926.01171875,7233.93994140625,0.0,535365.0,4394526.0,4694510000.0,425150000.0,89988400.0,0.0,368.0873718261719,78.80525970458984,4136.47998046875,33926.01171875,7233.93994140625,0.0,379.83499908447266,359.2560003662109,346.90124923706054,89.86800079345703,90.16340087890624,86.64570022583008,4029.480029296875,3932.3714306640622,3932.8894165039064,33792.555078125,33511.6903125,32495.514296875,7066.147534179688,6816.817626953125,6433.342590332031,0.0,0.0,0.0
```

## Reset
You can reset the market data by stopping the application and deleting the file `data/generated_data.csv`,
or generate new data for a company in Settings → Charts ("Modify").

The **Reset** button of the menu does not touch market data: it starts a new session for the participant
(starting money, no orders or shares, a new log folder). See [Export](#export).

## Generation
Market data is generated for each company according to the selected trend (Bull, Bear, Flat). The algorithm searches randomly in the CAC40 market data for trends that match the selected parameters.
### Parameters
- `Charts trends` : Select the number of trends you want to generate and their shape (Bull, Bear, or Flat).
- `Alpha` : The minimum percentage value of market change between the first and last day.
- `Length` : The number of days for the generated trend.
- `Start value` : The start value for the generated data.
- `Technical pattern (optional)` : a chart pattern drawn inside a trend: Double Top, Double Bottom,
  Head & Shoulders, Inverse Head & Shoulders, Ascending / Descending Triangle, Bullish / Bearish Flag,
  Cup & Handle, Rising / Falling Wedge.
- `Event overlay` : a sudden **Crash** or **Rally** added on top of the trends, with its `Position (%)`
  in the chart and its `Magnitude (%)`. A warning appears if the event starts inside a segment with a
  pattern, since the pattern's shape would be distorted.

After the market data is generated, news for these companies is generated in the background with the
settings of the News tab; a notification says when it is done.




# News

## Initialization
The news from real market data has been scraped in advance and is contained in a .csv file.

## Storage

### Path
The news data is stored in a CSV file.
Here is the file path: `data/news.csv`

### Format
The data saved for each ticker are as follows:
- `date`: The date of the data
- `ticker`: The company's ticker
- `title`: The title of the article
- `content`: The content of the article
- `sector`: The company's sector (Only if the news is generated)
- `sentiment`: The tone the article was asked to have, `positive` or `negative` (Only if the news is generated)
- `sentiment_label`: The tone FinBERT reads in the article: `strong positive`, `weak positive`,
  `neutral`, `weak negative` or `strong negative`. It decides the tag and colour shown to the
  participant and the notification filter (Only if the news is generated)

#### Columns
The columns of the file are those described above, separated by `;`.

#### Example
```csv
date;ticker;sector;title;content;sentiment
02/07/23 02:00;LVMH MOËT HENNESSY LOUIS VUITTON SE (MC);Textile Habillement Accessoires;LVMH : L'objectif de cours relevé à 740 E, une hausse de 14% attendue en 2024 !;UBS confirme son conseil à l'achat sur la valeur et relève son objectif de cours à 740 E (au lieu de 670 E) ce qui représente un potentiel de hausse de 14%. Nous nous attendons à ce que LVMH enregistre un bon début d'année 2024 avec une croissance des ventes et une dynamique continue en Asie, malgré les inquiétudes persistantes en Chine, défiant ainsi le contexte complexe du secteur. À moyen terme, en dépit des incertitudes économiques, géopolitiques et monétaires dans le monde, LVMH confirme un objectif de progression du chiffre d'affaires à taux constants ambitieux, et affirme 'aborder l'année 2024 avec confiance'.;positive
```

## Generation
News articles are written by an AI model, either in the cloud with **Groq** (free tier, needs an API
key) or on the computer with **Ollama**. The model is set in `.env` (`GROQ_MODEL`, default
`openai/gpt-oss-120b`; `OLLAMA_MODEL`, default `qwen3:8b`). Each article is placed where the price
moves enough (alpha) and written to match that move: positive when the price rises, negative when it
falls. Each company is assigned to a sector of activity, used in the article.

Each article is then checked by **FinBERT**, a second model that reads its tone (column
`sentiment_label`). The results are in `data/verification_report.csv`; without the FinBERT packages,
articles are marked `needs_review` (see README, "Generating news").

### Parameters
- `Choose how to generate news` : Local (Ollama) or Groq (Cloud). The Ollama URL and the Groq API key
  are read from `.env`; typing in the box overrides them.
- `Alpha` : The minimum percentage of market variation between two days required to place a news article.
- `Alpha interval` : The interval of days used to calculate the alpha variation.
- `Delta` : This value shifts the news by a certain number of days. For example, setting this to 1 will display the news one day earlier.

### Generation mode
- `Random mode` : choose how many positive and negative news to place, at random among the moves above alpha.
- `Linear mode` : place news on the moves above alpha in order. `Top-K` keeps only the K biggest
  price swings (0 = all).
- `Manual mode` : click on the chart (or pick a date) to place each positive or negative news yourself.
  Companies with manual positions use them instead of the automatic placement.




# Revenues

## Initialization
When you launch the application, revenues will be scraped using yahooquery and yfinance.
These are real data.

## Storage

### Path
The revenue data is stored in a CSV file.
Here is the file path: `data/revenue.csv`

Several companies can be saved at once in Settings → Revenues (this crashed before 30 Oct 2026).

### Format

The data saved for each ticker are as follows:
- `currencyCode`: the currency
- `NetIncome`: the company's net income (profit after all costs and taxes) for the year
- `TotalRevenue`: the company's total revenue (sales) for the year
- `asOfDate`: the end date of the financial year
- `symbol`: the ticker

The participant sees these as a bar chart (the revenue tab of the chart), only for the years that
ended before the current simulated date. Indexes have no revenue.

#### Index
- `currencyCode`: the currency
- `NetIncome`: net income
- `TotalRevenue`: total revenue

#### Columns
- `symbol`: the ticker
- `asOfDate`: the date of the data

#### Example 
```csv
symbol,ACA.PA,ACA.PA,ACA.PA,ACA.PA,AI.PA,AI.PA,AI.PA,AI.PA,AIR.PA,AIR.PA,AIR.PA,AIR.PA,BN.PA,BN.PA,BN.PA,BN.PA,BNP.PA,BNP.PA,BNP.PA,BNP.PA,CS.PA,CS.PA,CS.PA,CS.PA,DG.PA,DG.PA,DG.PA,DG.PA,DSY.PA,DSY.PA,DSY.PA,DSY.PA,EL.PA,EL.PA,EL.PA,EL.PA,KER.PA,KER.PA,KER.PA,KER.PA,MC.PA,MC.PA,MC.PA,MC.PA,OR.PA,OR.PA,OR.PA,OR.PA,RI.PA,RI.PA,RI.PA,RI.PA,RMS.PA,RMS.PA,RMS.PA,RMS.PA,SAF.PA,SAF.PA,SAF.PA,SAF.PA,SAN.PA,SAN.PA,SAN.PA,SAN.PA,STLAM.MI,STLAM.MI,STLAM.MI,STLAM.MI,STMPA.PA,STMPA.PA,STMPA.PA,STMPA.PA,SU.PA,SU.PA,SU.PA,SU.PA,TTE.PA,TTE.PA,TTE.PA,TTE.PA
asOfDate,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2019-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-06-30 00:00:00,2021-06-30 00:00:00,2022-06-30 00:00:00,2023-06-30 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00
currencyCode,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,USD,USD,USD,USD,EUR,EUR,EUR,EUR,USD,USD,USD,USD
NetIncome,2692000000.0,5844000000.0,5306000000.0,6348000000.0,2435100000.0,2572200000.0,2758800000.0,3078000000.0,-1133000000.0,4213000000.0,4247000000.0,3789000000.0,1956000000.0,1924000000.0,959000000.0,881000000.0,7067000000.0,9488000000.0,9848000000.0,10975000000.0,3857000000.0,3164000000.0,7294000000.0,6675000000.0,1242000000.0,2597000000.0,4259000000.0,4702000000.0,491000000.0,773700000.0,931500000.0,1050900000.0,85000000.0,1448000000.0,2152000000.0,2289000000.0,2150400000.0,3176000000.0,3614000000.0,2983000000.0,4702000000.0,12036000000.0,14084000000.0,15174000000.0,3563400000.0,4597100000.0,5706600000.0,6184000000.0,329000000.0,1305000000.0,1996000000.0,2262000000.0,1385000000.0,2445000000.0,3367000000.0,4311000000.0,352000000.0,43000000.0,-2459000000.0,3444000000.0,12294000000.0,6223000000.0,8371000000.0,5400000000.0,2173000000.0,14200000000.0,16799000000.0,18596000000.0,1106000000.0,2000000000.0,3960000000.0,4211000000.0,2126000000.0,3204000000.0,3477000000.0,4003000000.0,-7242000000.0,16032000000.0,20526000000.0,21384000000.0
TotalRevenue,18015000000.0,21397000000.0,20646000000.0,23455000000.0,20485200000.0,23334800000.0,29934000000.0,27607600000.0,49912000000.0,52149000000.0,58763000000.0,65446000000.0,23620000000.0,24281000000.0,27661000000.0,27619000000.0,52285000000.0,56355000000.0,57477000000.0,59735000000.0,124942000000.0,102897000000.0,111692000000.0,93083000000.0,44118000000.0,50230000000.0,62514000000.0,69885000000.0,4452200000.0,4860100000.0,5665200000.0,5951400000.0,14429000000.0,19820000000.0,24494000000.0,25395000000.0,13100200000.0,17645000000.0,20351000000.0,19566000000.0,44651000000.0,64215000000.0,79183000000.0,86153000000.0,27992100000.0,32287600000.0,38260600000.0,41182500000.0,8448000000.0,8824000000.0,10701000000.0,12137000000.0,6389000000.0,8981000000.0,11601000000.0,13427000000.0,16631000000.0,15133000000.0,19523000000.0,23651000000.0,37369000000.0,39175000000.0,45389000000.0,46444000000.0,47656000000.0,149419000000.0,179592000000.0,189544000000.0,10219000000.0,12761000000.0,16128000000.0,17286000000.0,25159000000.0,28905000000.0,34176000000.0,35902000000.0,119704000000.0,184634000000.0,263310000000.0,218945000000.0
```

## Generation

The data is not actually generated. It can be scraped or manually defined.

### Scrapping
We use yahooquery to retrieve the revenues of the ticker(s) between 2020 and the last year defined in the market data CSV (`data/generated_data.csv`).

> **WARNING**:
If the ticker does not exist in the real world, this will not work.

### Manual
You can enter the data manually in the interface.





# Companies

## Initialization
A list of companies and indexes are initially defined in the `defaults.py` file.

The data for these tickers will be scraped using yahooquery and yfinance.
You can add/remove companies in the `defaults.py` file before launching the application to scrape their real market data.

> **WARNING**:
> If you add companies after launching the application, you will need to add them manually in the configuration page.

> **WARNING**:
> If you add companies that do not exist in the real world, the market data cannot be scraped. This will result in an error.

## Storage
### Path
The data for companies/indices is stored in a Dash Store element (dcc.Store).
The data is thus stored locally in the client's browser.

### Format
The data is stored in a dictionary with the following keys:
- `label`: The name of the company or index
- `got_charts`: Whether the market data has been assigned (boolean)
- `activity`: The sector of activity of the company or "Index" if it is an index

The key of each dictionary corresponds to the Ticker.

#### Example
```python
companies = {
        "MC.PA": {
            "label": "LVMH MOËT HENNESSY LOUIS VUITTON SE (MC)",
            "activity": "Textile Habillement Accessoires",
            "got_charts": False,
        },
        "OR.PA": {
            "label": "L'ORÉAL (OR)",
            "activity": "Chimie Pharmacie Cosmétiques",
            "got_charts": False,
        },
         "^GSPC": {
            "label": "S&P 500",
            "activity": "Indice",
            "got_charts": True,
        },
    }
```

You can also create them in the configuration page by filling in the fields:
- `Company`
- `Ticker`
- `Sector`

Once this is done, you can generate market data and revenues for each Ticker.

> **WARNING**:
If you have not assigned market data to the ticker, you will not be able to generate revenues or news.
Thus, this Ticker will not be included in the simulation.




# Settings and features
The researcher sets these in the Configurator (`python app_config.py`, Settings page). Each setting
is saved in the browser and carried to the participants' computers in the
[session file](#session-file-sessionzip). Labels below are the English ones.

Every feature added during the 2026 internship is **off until the researcher turns it on**
(supervisors' decision, 30 Oct 2026): moving candles, random path, time reminders, leaderboard,
discrete mode, commission fee, chart Autoscale / Reset axes buttons. News pop-ups and news tags,
which existed before, stay on.

These defaults apply to a browser that has never saved the setting. A browser that has already
saved one keeps its value (the **Reset** button restarts the simulation, not the settings): change it
in Settings, or clear the browser's site data for the app.

## Settings → Advanced

| Setting | What it does | Default |
|---|---|---|
| Initial cashflow | Starting money of the participant | 100 000 € |
| Max requests | Most waiting orders at the same time | 10 |
| Session duration (minutes) | Real time the session lasts (timer mode) | 15 |
| Time between updates (ms), per candle step | Time between two chart updates | 5000 |
| Candles of history shown at the start | Past candles the participant sees before trading starts | 100 |
| Commission fee (%) | Paid on every executed buy and sell: with 0.05, buying 100 € costs 100.05 €, selling 100 € brings 99.95 € | 0 (no fee) |
| Moving candles | The newest candle forms in steps (every 30, 15 or 5 min of a 1 h candle) before it closes, like a live chart. "Off" = candles appear finished | Off |
| Price movement inside a forming candle | Only with moving candles. **Simple** or **Random**, see [below](#price-movement-inside-a-forming-candle) | Simple |
| News article font size | Small / Medium / Large | Small |
| Active companies | Companies the participant can trade (at least one) | all with market data |
| Dark mode for the simulation | Dark theme for the participant | off |
| Show the leaderboard | A ranking of the participant against 20 robot traders | off |
| Show the Autoscale and Reset axes buttons on the chart | The two buttons described in [Participant chart](#participant-chart) | off |

### Price movement inside a forming candle
The market data only has each candle's final Open, High, Low and Close, so the prices in between are
generated (`trade/utils/candle_steps.py`):
- **Simple**: Open → Low → High → Close for a rising candle (Open → High → Low → Close for a falling
  one), with a little noise.
- **Random** (added after the supervisors' answer, 30 Oct 2026): the High or the Low can come first,
  and the price wanders between them (a "Brownian bridge": a random walk whose start and end are
  fixed), like a leaf drifting down a river between its two banks.

Both always stay inside the real candle, reach its real High and Low, and end exactly on its Close.
The path is generated from a seed made of the company and the date, so every participant sees the
same one. The chart, the "market price" button, waiting orders and the leaderboard all use the
chosen path.

### Leaderboard
The 20 robots are made from the app's own prices: at the first candle each robot keeps 5–40 % of
the starting money as cash and buys a random mix of companies (paying the commission fee), then
never trades. A fixed seed gives every participant the same robots. Everyone is ranked by total
assets = cash + money put aside for waiting buy orders + shares' value. With moving candles, the
robots are valued at the price reached so far in the forming candle, like the participant
(`trade/utils/leaderboard.py`).

### Discrete mode (trials)
Instead of a running clock, the chart stops at fixed candles ("trials") and the participant moves on
with a **Next trial** button. Off by default.

- **Candles shown at each trial**: for example `10, 15` → trial 1 shows candles 1 to 10, trial 2 candles
  1 to 15. Whole numbers, each bigger than the one before. Saving also sets "Candles of history shown
  at the start" to the first number.
- Waiting orders are checked on every candle that a trial jumps over.
- No timer: the session ends after the last trial.
- **Confirmation**: "Next trial" first asks "Have you finished buying and selling for this trial? You
  cannot come back to it." ("No, stay" / "Yes, next trial"); on the last trial it asks to end the session.
- **No news pop-ups** in this mode (a trial can jump over many news at once); the news still appears in
  the news list.
- **Zoom on the candles while fewer than this are shown** (default 100): while fewer candles than this
  are shown, the chart is zoomed on them; from this number on it shows the whole session width.
  0 = always the whole session.

## Settings → News → Notifications

| Setting | What it does | Default |
|---|---|---|
| Show news notifications | Pop-ups when a news article appears | on |
| Show notifications for | Positive / negative / neutral news | all three |
| Days before news appears | Shows news this many days before its date (0 = same time) | 0 |
| Show time reminders | Pop-ups at 25 %, 50 %, 75 % of the session and at 5, 2 and 1 minutes left | off |
| Show sentiment tags and colours on news | Positive/negative tags and colours in the news list | on |

## Participant chart
The toolbar above the chart (zoom, pan, draw a line, zoom in/out) is always shown. The two buttons
below are only there when **Show the Autoscale and Reset axes buttons on the chart** is on
(Settings → Advanced, off by default).
- **Autoscale** (toolbar button or double-click): fits the candles shown, and keeps fitting them on
  every update.
- **Reset axes** (toolbar button): back to the starting view (the whole session width) and follows the
  live chart again, also while paused or after the end.
- A manual zoom or pan stays where the participant left it until one of these two buttons is used.
  Switching company always goes back to the starting view.
- Implemented in `trade/callbacks/dashboard/graph.py` (`track_graph_auto_follow`).

## End of the session
A results window shows the starting money, the final value and the profit or loss. The final value
counts cash, money put aside for buy orders still waiting, and the shares' value, the same total as
the portfolio and the leaderboard (`trade/callbacks/reset.py`).

## "Updating…" overlay (Configurator only)
While the Configurator is working for more than 0.3 s, the window is covered with a spinner and
"Updating…" ("Mise à jour…" in French), so the researcher doesn't click during an update, like a
loading screen in a game. It disappears as soon as the update ends. The participant app (Runtime)
has no overlay (`trade/app.py`, `_loading_overlay`).




# Session file (session.zip)
The researcher prepares the session in the Configurator, then clicks **Export Session** at the top of
the Settings page (enabled once market data exists). On each participant's computer, the Runtime
(`python app_runtime.py`) imports this file on the home page; **Start** stays disabled until a session
is imported.

The zip contains:
- `session.json`: every setting above (companies, starting money, max requests, update time, session
  duration, font size, theme, notifications on/off, notification filter and delay, moving candles,
  price movement inside a candle, chart buttons, candles of history, reminders, news tags, leaderboard, commission fee, discrete mode, trials, zoom);
- the data files `generated_data.csv`, `news.csv` and `revenue.csv` (`trade/utils/session.py`,
  `DATA_FILES`).

Older session files without a setting use the old behaviour for it (for example no leaderboard, no
fee, no zoom in discrete mode, Simple price movement, no chart buttons).

A test (`tests/test_session_zip.py`) checks that every setting the Configurator saves is exported and
imported, so a new setting can't be forgotten.




# Import

You can import market data, revenues, and news by importing CSV files formatted correctly:
- [Market](#format-)
- [News](#format)
- [Revenues](#format-1)

> **WARNING**:
To properly import your data, please use the `Import` tab on the configuration page.

#### Example
Importing market data through this page updates the `got_charts` field of the Store companies (see [Companies](#format-2)).


# Export
All the data used and generated are stored. We export the information of the interactions with the application, the portfolio, and the requests.

## Storage

### Path
The exported data is stored in 3 CSV files.
There are 3 files per session:
- `interface-logs.csv`: Interface logs
- `portfolio-logs.csv`: Portfolio logs
- `request-logs.csv`: Request logs

Each line of each CSV contains a UUID to link the logs together.

#### One folder per session
Each session writes its logs directly into its own folder, `data/exports/<session id>/`, for
example `data/exports/2026-10-07_10-15_a3f9/` (date, time and a short random part). A session
gets its ID when the dashboard opens; Reset or importing a session starts a new one. Every log
row has a `session-id` column, and `log-info.json` in the folder records the session ID, the
TradeSim code version and the settings. So participants' logs never mix, even if Reset is
forgotten or several participants use the same server.

Older sessions were first written to `data/export` and moved to a numbered folder
(`data/exports/1`, `2`, ...) on Reset; those folders are kept as they are.

### Triggers
One line is written to each of the three files every time the participant does something
(`trade/callbacks/dashboard/export.py`):
- When a news item is opened or closed
- When the request form switches between Buy and Sell
- When the chart switches between market data and revenue
- When the selected company changes
- When the list of waiting orders changes: an order is added, edited, executed or cancelled
- When one or all orders are deleted

The three lines of one trigger share the same `uuid`, so they can be joined.

Session events are also written to `interface-logs.csv`, with the event's name in the `form-action`
column: `session-start`, `session-pause`, `session-resume`, `next-trial` (discrete mode) and
`session-finish`.

With moving candles, `market-timestamp` includes the minutes reached inside the candle (e.g. 03:15),
not just the candle's date.

### interface-logs.csv
The saved data are as follows:
- `uuid`: The unique identifier of the trigger
- `session-id`: The session (same name as the folder)
- `market-timestamp`: The timestamp of the market data (the date of the simulation)
- `host-timestamp`: The timestamp of the interaction (the real date, in seconds since 1970)
- `cashflow`: The participant's cash
- `selected-company`: The selected company
- `form-action`: The state of the request form (`buy` or `sell`), or a session event
- `chart-type`: The selected chart (`market` or `revenue`)
- `is_news_description_displayed`: (bool) If a news item was clicked to display the description
- `news_title`: The title of the clicked news item, or empty

#### Example
```csv
uuid,session-id,market-timestamp,host-timestamp,cashflow,selected-company,form-action,chart-type,is_news_description_displayed,news_title
6bcf94a5-a75e-4d98-8115-8eb1fb87b340,2026-10-29_22-30_1e98,2025-08-11 03:00:00+02:00,1793309455.129577,100000,MC.PA,buy,market,False,
```

### portfolio-logs.csv
The saved data are as follows:
- `uuid`: The unique identifier of the trigger
- `session-id`: The session
- `[Ticker]-shares`: The number of shares of the ticker
- `[Ticker]-totals`: The total value of the shares of the ticker

#### Example
```csv
uuid,session-id,MC.PA-shares,OR.PA-shares,...,MC.PA-totals,OR.PA-totals,...
6bcf94a5-a75e-4d98-8115-8eb1fb87b340,2026-10-29_22-30_1e98,0,0,...,0,0,...
```

### request-logs.csv
The saved data are as follows:
- `uuid` : The unique identifier of the trigger
- `session-id`: The session
- `deleted-request` : The indexes of the deleted requests (`["all"]` when all are deleted)
- `request-[n]` : The waiting orders: [action] [price] [quantity] [ticker], one column per order up to "Max requests"

#### Example
```csv
uuid,session-id,deleted-request,request-1,request-2,request-3,request-4,request-5,request-6,request-7,request-8,request-9,request-10
62cffea7-2113-498f-aef9-fa6963640406,2026-10-29_22-30_1e98,[0],buy 1000 1 MC.PA,buy 1000 1 MC.PA,,,,,,,,
```

### log-info.json
Written in the session's folder each time the session starts: the session ID, the log format version,
and for each start the time, the TradeSim code version (git commit) and all the settings used. It
answers "which settings and which version produced these logs?".

### When the columns change
If the companies or the settings change during a session, a log file is rewritten with all the
columns, old rows getting empty cells for the new ones, so no value ends up under the wrong header.
A file damaged by an older version is left untouched and the new rows go to a new part, e.g.
`portfolio-logs-2.csv` (`trade/utils/export.py`, `save_df`).

