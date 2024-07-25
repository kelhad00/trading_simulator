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
Run the following command in the root folder:
```bash
cd trade
python app.py
```

## Requirements
- Python 3.10
- Packages in `requirements.txt`


## Structure
### Files
- `app.py` : main file to run the application and contains the stores
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


