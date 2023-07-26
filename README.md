<!-- References -->
[repo-url]: https://github.com/kelhad00/trading_simulator/ "Project repository"
[sensors-repo-url]: https://github.com/kelhad00/multisensor_biosignal_toolkit "Project repository with sensors"

[library-exemple-url]: https://github.com/kelhad00/trading_simulator/blob/main/main.py "Sample file to start the interface"
[requirements-url]: https://github.com/kelhad00/trading_simulator/blob/main/requirements.txt "Project requirements"

[dash-projet-url]: https://github.com/plotly/dash "dash project repository we use"
[dash-documentation-url]: https://dash.plotly.com/reference#dash.dash "Dash object documentation"

<!-- [discussion-url]: https://github.com/kelhad00/trading_simulator/discussions "Project thread" -->
[wiki-url]: https://github.com/kelhad00/trading_simulator/wiki "Project wiki page"
<!-- [license-url]: https://github.com/kelhad00/trading_simulator/blod/main/LICENSE "Project license" -->


# emotrade

A stock market site simulator for collecting data on stocks carried out by the trader.

![emotrade interface home page](https://github.com/kelhad00/trading_simulator/blob/main/.github/images/homepage.png)

![emotrade interface dashboard](https://github.com/kelhad00/trading_simulator/blob/main/.github/images/dashboard.png)

This simulation takes stock market data for a given period and presents it in an interface that evolves with time and the user's actions.

The interface allows you to make buy or sell requests on a company's shares, view the company's share price and earnings per year via graphs, know your stock portfolio and consult the news.
It's currently available in English and French, and we'd be delighted to extend it to more languages (see the [contributing](#contributing) section).

The user's actions are recorded throughout the simulation in a data file in .csv format, enabling you to study the trader's behavior during the simulation.


## Table of contents

- [Requirements](#requirements)
- [Installing](#installing)
- [Usage](#usage)
    - [Using the command line tool](#using-the-command-line)
    - [Using it as a library](#integrating-it-into-your-program)
- [Handling the application](#handling-the-application)
    - [Modify default configuration](#default-configuration)
    - [Modify running application](#modify-application-status-during-operation)
    - [Dash object below app object](#dash-object-below-app-object)
- [The Setup toolbox](#the-setup-toolbox)
- [Structure of data](#structure-of-data)
    - [The generated data: interface-logs](#the-data-generated)
    - [News file](#structure-of-the-news-file)
    - [Market data file](#market-data-file-structure)
    - [Revenue file](#revenue-file-structure)
- [Why was this project created?](#why-was-this-project-created)
- [Contributing](#contributing)


## Requirements

- [Python](https://www.python.org/) == 3.10 (Has not been tested for more recent versions)
- [dash][dash-projet-url] >= 2.10.2 : Low-code framework for rapidly building data apps in Python.
- [Pandas](https://pandas.pydata.org/) >= 2.0.2 : Fast, powerful, flexible and easy to use open source data analysis and manipulation tool

### Optional (if you want to use `emotrade.setup` tools)
- [yahooquery](https://yahooquery.dpguthrie.com/) >= 2.3.1 : Python wrapper for an unofficial Yahoo Finance API

The complete list is in [requirements.txt][requirements-url]


## Installing

<!-- Install and update using pip:
```bash
pip install -U emotrade
``` -->

Download the latest version of the repository and install the package locally with pip:
```bash
# Clone the repository or download the latest version on the corresponding page
cd trading_simulator # Move to project root
pip install setuptools . # Don't forget the dot at the end to install emotrade from local files
```

If you need the `Setup` toolkit, also install the additional dependencies:
```bash
pip install setuptools .[extra]
```

## Usage
### Using the command line

Simply use the command line tool.
```bash
emotrade <data_directory>
```

For more information on the command line :
```bash
emotrade -h
```

### Integrating it into your program

If you want to integrate it into your program, here's a simple example:
```python
# main.py
from emotrade import app
from emotrade.Setup import download_market_data

download_market_data() # Prepare the minimum necessary for interface operation

# [Your program...]

app.set_layout() # Import the layout before starting the server
app.run_server() # Server startup blocks the next instruction until the user presses ctrl-c in the terminal.
```

For a more realistic example, have a look at the [`main.py`][library-exemple-url] file in this repository.

For more complex use, with other instructions during server operation, it's best to put your program in a different thread. Like this:
```python
# main.py
from threading import Thread
from emotrade import app

download_market_data() # Prepare the minimum necessary for interface operation

# [A few instructions before getting started...]

th = Thread(target=your_program)
th.start()

app.set_layout() # Import the layout
app.run_server() # Starts the server and blocks the following instructions.
```


## Handling the application

The application can be fully manipulated using the `app` object available from `emotrade`.

### Default configuration

The default values are available from `app.defaults` or its abbreviated version `app.d`. It is strongly recommended not to modify them after calling `app.set_layout()` and/or `app.run_server()`.

Here is a description of the default values used:
```python
# Period of time used to update data on the dashboard
app.d.update_time = 60*1000 # in milliseconds

# Maximum number of requests the user can make on the dashboard
app.d.max_requests = 10

# Initial money the user has
app.d.initial_money = 100000

# Path to the data folder
app.d.data_path = "Data"

# Stocks used in the interface
# They are also used to download data with the download_market_data setup tool
# The key is the ticker and the value is the name of the company
# So the data provided in the Data folder must have the same name as the symbol
app.d.companies = {
    "MC.PA" : "LVMH MOËT HENNESSY LOUIS VUITTON SE (MC)",
    "OR.PA" : "L'ORÉAL (OR)",
    "RMS.PA" : "HERMÈS INTERNATIONAL (RMS)",
    "TTE.PA" : "TOTALENERGIES SE (TTE)",
    "SAN.PA" : "SANOFI (SAN)",
    "AIR.PA" : "AIRBUS SE (AIR)",
    "SU.PA" : "SCHNEIDER ELECTRIC SE (SU)",
    "AI.PA" : "AIR LIQUIDE (AI)",
    "EL.PA" : "ESSILORLUXOTTICA (EL)",
    "BNP.PA" : "BNP PARIBAS (BNP)",
    "KER.PA" : "KERING (KER)",
    "DG.PA" : "VINCI (DG)",
    "CS.PA" : "AXA (CS)",
    "SAF.PA" : "SAFRAN (SAF)",
    "RI.PA" : "PERNOD RICARD (RI)",
    "DSY.PA" : "DASSAULT SYSTÈMES SE (DSY)",
    "STLAM.MI" : "STELLANTIS N.V. (STLAM)",
    "BN.PA" : "DANONE (BN)",
    "STMPA.PA" : "STMICROELECTRONICS N.V. (STMPA)",
    "ACA.PA": "CRÉDIT AGRICOLE S.A. (ACA)"
}

# Indexes used in the interface
# Same use as the companies variable
app.d.indexes = {
    "^GSPC" : "S&P 500",
    "^DJI" : "Dow Jones Industrial Average",
    "^FCHI" : "CAC 40",
    "^SPGSGC" : "S&P GSCI Gold Index",
}
```

### Modify application status during operation

The `app` object also provides variables for manipulating the interface and/or finding out the state of an element while the interface is running.

These variables and their default values are described below:
```python
# Enables or disables the start button on the home page.
# Takes a Boolean as input
app.home_start_button_disabled = false

# Describe the state of the application,
# i.e. whether the dashboard is displayed or not.
# This variable is set when the user arrives on a page.
# It is therefore undefined until this happens.
app.dashboardIsRunning
```

### Dash object below app object

The `app` object we provide is actually a `Dash` object, taken from the [`dash`][dash-projet-url] library, to which we have added our own functionalities, and therefore contains all the features of this object. Please refer to the corresponding [documentation][dash-documentation-url] for more information on all the features of this object.


## The `Setup` toolbox

The `emotrade.Setup` toolbox provides additional functions for creating an interface environment.
Here's a list:

```python
def download_market_data():
    """ Download daily stock market data for companies and indexes
        defined respectively by `app.d.companies` and `app.d.indexes`
        over the last two years, then save them in the folder defined
        by `app.d.data_path`.
    """
    pass

def analyse_news_data(data_path='Data'):
    """ Opens a jupyter notebook at the location
        defined by the data_path argument
        to analyze the data it contains in the form of graphs.
    """
    pass

```

For legal reasons, we do not provide a way to generate the news.csv file. It is up to you to obtain this file and place it in the folder defined by `app.d.data_path`. It must contain the columns `title;content;ticker;date` with the separator ";".


## Structure of data

All the data used and generated is stored in a specific folder defined by the [`app.d.data_path`](#default-configuration) variable. This data has a constant structure, as explained below.

### The data generated

Once launched, the interface generates an `interface-logs.csv` file in the same folder as the other data (by default: `Data`), containing all the activity on the dashboard page. This file is structured so that there is only one item of data per column, with :
- the `host-timestamp` column gives the timestamp of the host machine, which allows this data to be synchronised with other data.
- the `market-timestamp` column gives the timestamp of the data displayed on the interface.
- the `<TICKER>-shares` columns contain the shares owned by the user.
- the `<TICKER>-total` columns contain the value of all the shares owned at a given time.
- the `cashflow` column corresponds to the money that the user can use.
- the `selected-company` column indicates the ticker of the share displayed on the charts at a given time.
- the `request <N>` columns contain the Nth request in the list of requests waiting to be completed.
- the `nbr-news-displayed` and `last-news` columns respectively designate the number of news items displayed in the news table and the most recent news item displayed.
- the `news-mode` and `selected-graph` columns respectively designate what is displayed in the news part and the graph part.
- the `selected-news` column is empty when `news-mode` is equal to `news-table` and gives the title of the news displayed when `news-mode` is equal to `news-description`.

### Structure of the news file

To display news in the news table, the interface needs a `news.csv` file containing at least these three columns separated by a semicolon:
- `title` or `article` which contains the title of the article to be displayed, and which is used in the news table when displaying the list or at the top when displaying the article description.
- `content` contains the article content, which will be displayed when the user clicks on the article title.
- `date` which contains the date and time (optional) of the news item. The date must be formalized with the day first, i.e. {day}/{month}/{year}.

### Market data file structure

If you'd like to use your own market data instead of that generated by the [`download_market_data`](#the-setup-toolbox) setup tool, or if you'd like to understand the structure of the `market_data.csv` file, this file has two header lines, the first of which contains the ticker and the second the data type, for each of the companies and indexes you wish to display. This file uses a date column as index and a comma separator.
The data types required are `Open`, `High`, `Low`, `Close`, `long_MA` and `short_MA`.
Here's an example to help you understand:
```csv
symbol,MC.PA,MC.PA,MC.PA,MC.PA,MC.PA,MC.PA,^SPGSGC,^SPGSGC,^SPGSGC,^SPGSGC,^SPGSGC,^SPGSGC,^SPGSGC
      ,Open,High,Low,Close,long_MA,short_MA,Open,High,Low,Close,long_MA,short_MA                   [...]
date,,,,,,,,,,,,
[...]
```

If this still isn't clear to you. Use the [`download_market_data`](#the-setup-toolbox) setup tool to generate a complete file. I hope this helps.

### Revenue file structure

If you wish to use your own revenue data instead of that generated by the [`download_market_data`](#the-setup-toolbox) setup tool, or if you want to understand the structure of the `revenue.csv` file, this file contains a line for:
- `asOfDate` which contains the data date
- the `symbol` contains the company identifier or index and must be identical to that supplied by the [`app.d.companies` and `app.d.indexes`](#default-configuration) variables respectively.
- `NetIncome` and `Total revenue` each contain the value associated with it for each ticker and date.
Here's an example to help you understand:

```csv
symbol,ACA.PA,ACA.PA,ACA.PA,ACA.PA [...]
asOfDate,2019-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00 [...]
NetIncome,4844000000.0,2692000000.0,5844000000.0,5437000000.0 [...]
TotalRevenue,19123000000.0,18061000000.0,21397000000.0,21955000000.0 [...]
```

If this still isn't clear to you. Use the [`download_market_data`](#the-setup-toolbox) setup tool to generate a complete file. I hope this helps.


## Why was this project created?

In the financial laboratories of the University of Mons, a study has been launched to analyse the reactions of traders to the stock markets. To better understand which factors are most important in their choices, what is the "human" part of this equation, and many other questions. To improve their results, the researchers needed to create a controlled, automated data-gathering environment. `emotrade` is an independent part of this environment, to which several sensors have been added. To find out more, have a look at the corresponding repository [here][sensors-repo-url].


<!-- ## Wiki

Check out the [wiki][wiki-url] for more info. -->


## Contributing

Feel free to create an issue/PR if you want to see anything else implemented.
<!-- If you have some question or need help with configuration, start a [discussion][discussion-url]. -->

<!-- Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a PR. -->
<!-- You can also help with documentation in the [wiki][wiki-url]. -->


<!-- ## Legal Stuff

**emotrade** is distributed under the <Add license here> license. See the [LICENSE][license-url] file in the release for details. -->
