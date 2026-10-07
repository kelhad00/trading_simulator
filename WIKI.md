
## Wiki
- [Market](#market)
- [News](#news)
- [Revenues](#revenues)
- [Companies](#companies)
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
You can reset the market data by cutting the application and deleting the file `data/generated_data.csv`
> **TODO** :
> Add a reset button in the interface

## Generation
Market data is generated for each company according to the selected trend (Bull, Bear, Flat). The algorithm searches randomly in the CAC40 market data for trends that match the selected parameters.
### Parameters
- `Charts trends` : Select the number of trends you want to generate and their shape (Bull, Bear, or Flat).
- `Alpha` : The minimum percentage value of market change between the first and last day.
- `Length` : The number of days for the generated trend.
- `Start value` : The start value for the generated data.




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
- `sentiment`: The sentiment of the article (Only if the news is generated)

#### Columns
The columns of the file are those described above.

#### Example
```csv
date;ticker;sector;title;content;sentiment
02/07/23 02:00;LVMH MOËT HENNESSY LOUIS VUITTON SE (MC);Textile Habillement Accessoires;LVMH : L'objectif de cours relevé à 740 E, une hausse de 14% attendue en 2024 !;UBS confirme son conseil à l'achat sur la valeur et relève son objectif de cours à 740 E (au lieu de 670 E) ce qui représente un potentiel de hausse de 14%. Nous nous attendons à ce que LVMH enregistre un bon début d'année 2024 avec une croissance des ventes et une dynamique continue en Asie, malgré les inquiétudes persistantes en Chine, défiant ainsi le contexte complexe du secteur. À moyen terme, en dépit des incertitudes économiques, géopolitiques et monétaires dans le monde, LVMH confirme un objectif de progression du chiffre d'affaires à taux constants ambitieux, et affirme 'aborder l'année 2024 avec confiance'.;positive
```

## Generation
News articles are generated using Llama3 and a dataset of news articles scraped from abcbourse.com. The LLM takes a news article from the same activity sector as the company in the dataset and reformulates it. The news will then be displayed either randomly or sequentially, depending on the selected mode, when a variation meets the specified parameters (alpha & alpha interval).

### Parameters
- `API key` : Enter your Groq API key for news generation.
- `Alpha` : The minimum percentage of market variation between two days required to display a news article.
- `Alpha interval` : The interval of days used to calculate the alpha variation.
- `Delta` : This value shifts the news by a certain number of days. For example, setting this to 1 will display the news one day earlier.

Each company is assigned to a sector of activity. The news generated will be from the same sector as the company.




# Revenues

## Initialization
When you launch the application, revenues will be scraped using yahooquery and yfinance.
These are real data.

## Storage

### Path
The market data is stored in a CSV file.
Here is the file path: `data/revenues.csv`

### Format

The data saved for each ticker are as follows:
- `currencyCode`: the currency
- `NetIncome`:
- `TotalRevenue`: 
- `asOfDate`: the year of the data 
- `symbol`: the ticker 

#### Index 
- `currencyCode`: the currency
- `NetIncome`:
- `TotalRevenue`:

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
The data is exported every time an action is performed by the user.
- When a news item is clicked or closed
- When an action is performed on the request form (change of action type)
- When the type of chart changes (Market Data or Revenues)
- When the selected ticker changes
- When a request is added
- When a request is deleted
- When an action is performed on the portfolio (Buy or Sell)
- When the market data timestamp changes



### interface-logs.csv 
The saved data are as follows:
- `uuid`: The unique identifier of the session (trigger)
- `market-timestamp`: The timestamp of the market data (the date of the simulation)
- `host-timestamp`: The timestamp of the interaction (the real date)
- `cashflow`: The user's cashflow
- `selected-company`: The selected company
- `form-action`: The state of the request form (Buy or Sell)
- `chart-type`: The selected chart type (Market Data or Revenues)
- `is_news_description_displayed`: (bool) If a news item was clicked to display the description
- `news_title`: The title of the clicked news item or None

#### Example
```csv
uuid,market-timestamp,host-timestamp,cashflow,selected-company,form-action,chart-type,is_news_description_displayed,news_title
6ab4129b-1d72-410b-bed8-6e001bed8a85,2005-04-30T00:00:00,1721135847.22061,100000,OR.PA,sell,market,False,
```

### portfolio-logs.csv
The saved data are as follows:
- `uuid`: The unique identifier of the session (trigger)
- `[Ticker]-shares`: The number of shares of the ticker
- `[Ticker]-totals`: The total value of the shares of the ticker

#### Example
```csv
uuid,MC.PA-shares,OR.PA-shares,RMS.PA-shares,TTE.PA-shares,SAN.PA-shares,AIR.PA-shares,SU.PA-shares,AI.PA-shares,EL.PA-shares,BNP.PA-shares,KER.PA-shares,DG.PA-shares,CS.PA-shares,SAF.PA-shares,RI.PA-shares,DSY.PA-shares,STLAM.MI-shares,BN.PA-shares,STMPA.PA-shares,ACA.PA-shares,^GSPC-shares,^DJI-shares,^FCHI-shares,^SPGSGC-shares,MC.PA-totals,OR.PA-totals,RMS.PA-totals,TTE.PA-totals,SAN.PA-totals,AIR.PA-totals,SU.PA-totals,AI.PA-totals,EL.PA-totals,BNP.PA-totals,KER.PA-totals,DG.PA-totals,CS.PA-totals,SAF.PA-totals,RI.PA-totals,DSY.PA-totals,STLAM.MI-totals,BN.PA-totals,STMPA.PA-totals,ACA.PA-totals,^GSPC-totals,^DJI-totals,^FCHI-totals,^SPGSGC-totals
8ae40745-8d76-4cd8-b3f3-c2b8d229e7fb,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

### request-logs.csv
The saved data are as follows:
- `uuid` : The unique identifier of the line (trigger)
- `deleted-request` : The indexes of the deleted requests
- `request-[n]` : The user's requests: [action] [price] [quantity] [ticker]

#### Example
```csv
uuid,deleted-request,request-1,request-2,request-3,request-4,request-5,request-6,request-7,request-8,request-9,request-10
62cffea7-2113-498f-aef9-fa6963640406,[0],buy 1000 1 MC.PA,buy 1000 1 MC.PA,buy 1000 1 MC.PA,,,,,,,
```

