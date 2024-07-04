translation = {
    'en': {
        # Portfolio
        "portfolio": "Portfolio",
        'portfolio-columns': {'Stock': 'Stocks', 'Shares': 'Shares', 'Total': 'Price'},
        "portfolio-cashflow": "Cashflow: ",
        "portfolio-investment": "Total investment: ",

        # Company graph
        "tab-market": "Technical Analysis",
        "tab-revenue": "Revenue",
        "market-graph": {
            'x': 'Date',
            'y': 'Price',
            'legend': {
                'longMA': ' Simple moving average (20)',
                'shortMA': ' Simple moving average (50)',
                'twohunMA': ' Simple moving average (200)', 
                'price': 'Price'
            },
        },
        "revenue-graph": {
            "totalRevenue": "Revenue",
            "netIncome": "Income"
        },

        # News table
        "news": "Market News",
        "news-table": {
            "date": "Date",
            "article": "Article"
        },

        # News description
        "title-news-description": "Article Description",
        "button-news-description": "Close",

        # Request form
        "request-title": "Make a Request",
        "request-action": {
            "label": "Action",
            # "choices": {'sell': 'Sell', 'buy': 'Buy'}
            "choices": [{
                "label": "Sell",
                "value": "sell"
            }, {
                "label": "Buy",
                "value": "buy"

            }]
        },
        "request-price": "Price",
        "request-shares": "Number of Shares",
        "submit-request": "Submit",
        "err-too-many-requests": "You have too many requests !",
        "err-wrong-form": "Please enter a valid price !",
        "err-enough-money": "You don't have enough money !",
        "err-enough-shares": "You don't have enough shares of {} !",

        # Requests list
        "requests-list-title": "Request List",
        "requests-table": {
            "actions": "Type",
            "shares": "Shares",
            "company": "Stocks",
            "price": "Price"
        },
        "clear-all-requests-button": "Clear All",
        "clear-requests-button": "Clear",

        # Home Page
        "button-start": "Start Session",
        "button-settings" : "Settings",
        "button-restart-sim": "Reset",
        "welcome": ["Welcome to", "TradeSim"],
        "description": ["Click on ", "'Start Session'", ", to start the session. The interface is available in ", "english ", "and ", "french", "."],

        # Settings Page
        "settings-title": "Settings",
        "settings-subtitles": {
            "market-data": "Market data creation",
            "charts-trends": "Charts trends",
            "charts-patterns": "Stock choice",
            "final-charts": "Preview",
            "generate-modal": "Generate market data"

        },
        "settings-sliders": {
            "alpha": "Select alpha value",
            "length": "Select length of a market movement"
        },
        "settings-radio": {
            "trend": "Select a trend",
            "options": ["Bull 📈", "Bear 📉", "Flat"]
        },
        "settings-button": {
            "modify": "Modify",
            "select-all": "Select all",
            "add": "Ajouter"
        },
        "settings-number-inputs": {
            "number-trends": "Number of charts trends",
            "number-patterns": "Select a stock"
        },
        "settings-timeline": "market movement",
        "settings-stocks-input": {
            "company": "Company",
            "ticker": "Ticker",
            "activity": "Activity"
        },
        "settings-tabs": {
            "stock": "Stocks",
            "chart": "Charts",
            "news": "News"
        },

    }
}