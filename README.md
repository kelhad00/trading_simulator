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


## Structure
### Files
- `app.py` : main file to run the application
- `callbacks` : folder containing all the callbacks (dynamic functions, user interactions)
- `components` : folder containing all the static & reusable front-end elements
- `layouts` : folder containing all the layouts of the application
- `assets` : folder containing all the static files (css, images, etc.)
- `locales` : folder containing all the translations for each language
- `pages` : folder containing all the pages of the application. import the layouts and specific callbacks files.
- `utils` : folder containing all the static & utility functions
- `defaults.py` : file containing all the default values for the application
### Styling
- `Tailwind CSS` is used for the styling of the application. (https://tailwindcss.com/)
- `Dash Mantine Components` is used for the visual components. (version 1.12) (https://dmc-docs-0-12.onrender.com/)


## Synthetics data
### News
News articles are generated using Llama3 and a dataset of news articles scraped from abcbourse.com. The LLM takes a news article from the same activity sector as the company in the dataset and reformulates it. The news will then be displayed either randomly or sequentially, depending on the selected mode, when a variation meets the specified parameters (alpha & alpha interval).
#### News parameters
- `API key` : Enter your Groq API key for news generation.
- `Alpha` : The minimum percentage of market variation between two days required to display a news article.
- `Alpha interval` : The interval of days used to calculate the alpha variation.
- `Delta` : This value shifts the news by a certain number of days. For example, setting this to 1 will display the news one day earlier.

### Market data
Market data is generated for each company according to the selected trend (Bull, Bear, Flat). The algorithm searches randomly in the CAC40 market data for trends that match the selected parameters.
#### Parameters
- `Charts trends` : Select the number of trends you want to generate and their shape (Bull, Bear, or Flat).
- `Alpha` : The minimum percentage value of market change between the first and last day.
- `Length` : The number of days for the generated trend.
- `Start value` : The start value for the generated data.