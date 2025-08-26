## Wiki

* [Market](#market)
* [Generation](#generation)
* [News](#news)
* [Revenues](#revenues)
* [Companies](#companies)
* [Import](#import-)
* [Export](#export)

# Market

Market data can be configured for each ticker in the "Charts" section of the configuration page.

## Initialization

When you launch the application, no real data is automatically loaded.
Data must be generated (see [Generation](#generation)) or imported (see [Import](#import-)).

## Storage

### Path

Market data is stored in a CSV file.
Path: `data/generated_data.csv`

### Format

The data saved for each ticker includes:

* `Open` : Opening price
* `High` : Highest price
* `Low` : Lowest price
* `Close` : Closing price
* `Volume` : Daily trading volume
* `adjclose` : Adjusted price
* `long_MA` : Long-term moving average
* `short_MA` : Short-term moving average
* `200_MA` : 200-day moving average

#### Index

* `date` : Date of the data point

#### Columns

* `symbol` : Company ticker
* `None` : Data columns (Open, High, Low, Close, Volume, adjclose, long\_MA, short\_MA, 200\_MA)

#### Example

```csv
symbol,OR.PA,SAN.PA
,Open,High
date,,
2023-02-03 01:00:00+01:00,375.5,384.3
```

## Reset

You can reset market data by stopping the application and deleting the file `data/generated_data.csv`.

# Generation

Market data generation is done **by blocks** directly on a timeline.
Each block corresponds to a trend (Bull, Bear, or Flat) and can be manipulated visually.

## Features Implemented

* **Add blocks**: Insert a new block with a chosen trend (Bull, Bear, or Flat).
* **Delete blocks**: A block can be removed from the timeline.
* **Resize**: A block’s duration (Length) can be adjusted by dragging its left/right handles.
* **Configure via modal**: Some blocks have a configuration window accessible by button.

## Block Parameters

* **Trend**: Bull / Bear / Flat
* **Intensity**: Small / Medium / Very
* **Length**: Number of days of the block, relative to its size in the timeline

## Patterns

In the block configuration, it is possible to:

* Choose **insertion type**: with pattern or without pattern
* Select **patterns** to include
* Use two modes:

  * **Type**: simple selection of patterns
  * **Type & Quantity**: selection of patterns with the desired quantity for each

# News

## Initialization

News data from real markets has been stored in a `.csv` file.

## Storage

### Path

News data is stored in a CSV file:
`data/news.csv`

### Format

* `date` : Date of the news
* `ticker` : Company ticker
* `title` : News title
* `content` : News content
* `sector` : Company sector (only if generated)
* `sentiment` : Sentiment of the article (only if generated)

#### Example

```csv
date;ticker;sector;title;content;sentiment
02/07/23 02:00;LVMH (MC);Textiles Apparel Accessories;LVMH: Target price raised to €740;UBS maintains its buy rating...;positive
```

## Generation

News articles are generated using **Llama3** and a dataset of articles.
The model reformulates an article from the same sector as the company.
News can be displayed randomly or sequentially depending on the selected mode.

### Parameters

* `API key` : Groq API key for news generation
* `Alpha` : Minimum market variation between the first and last day
* `Alpha interval` : Interval of days used to calculate variation
* `Delta` : News shift (e.g. `1` = show one day earlier)
* `Mode` : Display mode (Random or Sequential)

# Revenues

## Initialization

Revenues are not generated automatically.
They can be added **manually** via the interface or **imported** from a CSV.

## Storage

### Path

Revenue data is stored in:
`data/revenues.csv`

### Format

* `currencyCode` : Currency
* `NetIncome` : Net income
* `TotalRevenue` : Total revenue
* `asOfDate` : Year of the data
* `symbol` : Ticker

#### Example

```csv
symbol,ACA.PA,AI.PA
asOfDate,2020-12-31,2021-12-31
currencyCode,EUR,EUR
NetIncome,2692000000.0,5844000000.0
TotalRevenue,18015000000.0,21397000000.0
```

## Generation

Revenue data can be defined manually in the interface.

# Companies

## Initialization

A list of companies and indexes is initially defined in the file `defaults.py`.
You can also create new ones in the configuration page.

## Storage

Data is stored in a Dash `dcc.Store`, on the client (browser).

### Format

* `label` : Company or index name
* `got_charts` : Boolean indicating if market data has been assigned
* `activity` : Activity sector (or "Index" for an index)

#### Example

```python
companies = {
    "MC.PA": {
        "label": "LVMH",
        "activity": "Textiles Apparel Accessories",
        "got_charts": False,
    },
    "OR.PA": {
        "label": "L'ORÉAL",
        "activity": "Chemicals Pharmaceuticals Cosmetics",
        "got_charts": False,
    },
}
```

> **WARNING**: If you have not assigned market data to a ticker, you will not be able to generate its revenues or news.

# Import

You can import market data, revenues, and news through properly formatted CSV files.

# Export

All used and generated data is exported.
This includes interactions with the application, the portfolio, and the requests.

Data is exported as CSV files:

* `interface-logs.csv`
* `portfolio-logs.csv`
* `request-logs.csv`

Each session is identified by a unique **UUID**.
