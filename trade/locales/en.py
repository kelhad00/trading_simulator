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

        "settings": {
            "title": "Settings",
            "tabs": {
                "ticker": "Tickers",
                "chart": "Charts",
                "news": "News",
                "advanced": "Advanced",
                "revenues": "Revenues",
                "import": "Import",
            },
            "charts": {
                "subtitles": {
                    "modal": "Market data creation",
                    "ticker": "Stock choice",
                    "preview": "Preview",
                    "parameters": "Market movement parameters",
                    "trends": "Charts trends",
                    "curve": "Growth curve profile",
                },
                "button": {
                    "modify": "Modify",
                    "delete": "Delete",
                    "select-all": "Select all",
                },
                "select": {
                    "ticker": "Select a stock",
                    "alpha": "Select alpha value",
                    "length": "Select length of a market movement",
                    "start": "Select start date",
                    "curve-profile": "Growth curve profile",
                    "noise": "Noise / volatility level (%)",
                    "crash-point": "Crash point (% of duration)",
                },
                "curve-profiles": {
                    "segments": "Market segments",
                    "linear": "Linear",
                    "exponential": "Exponential",
                    "logarithmic": "Logarithmic",
                    "volatile": "Volatile",
                    "crash": "Crash",
                },
                "radio": {
                    "title": "market movement",
                    "label": "Select a trend",
                    "options": ["Bull 📈", "Bear 📉", "Flat"],
                },
                "input": {
                    "trends": "Number of charts trends",
                },
                "pattern-select": {
                    "label": "Technical pattern (optional)",
                    "none": "None",
                    "double_top": "Double Top",
                    "double_bottom": "Double Bottom",
                    "head_and_shoulders": "Head & Shoulders",
                    "inverse_head_and_shoulders": "Inverse Head & Shoulders",
                    "ascending_triangle": "Ascending Triangle",
                    "descending_triangle": "Descending Triangle",
                    "bullish_flag": "Bullish Flag",
                    "bearish_flag": "Bearish Flag",
                    "cup_and_handle": "Cup & Handle",
                    "rising_wedge": "Rising Wedge",
                    "falling_wedge": "Falling Wedge",
                },
            },
            "tickers": {
                "subtitles": {
                    "form": "Add a ticker",
                    "list": "Stocks",
                },
                "button": {
                    "add": "Add",
                    "reset": "Reset",
                    "edit": "Edit",
                    "save": "Save",
                },
                "input": {
                    "company": "Company",
                    "ticker": "Ticker",
                    "activity": "Activity",
                    "description": "Description (optional)",
                },
                "description-placeholder": "e.g. Global luxury goods conglomerate specialising in fashion, leather goods, perfumes and cosmetics.",
                "notification": {
                    "success-title": "Renamed",
                    "success-msg": "{ticker} has been renamed to \"{name}\"",
                    "error-title": "Error",
                    "error-msg": "Company name cannot be empty",
                },
                "validation": {
                    "missing-label-title": "Validation",
                    "missing-label-msg": "All active companies must have a name before starting the simulation.",
                },
            },
            "news": {
                "subtitles": {
                    "key": "Groq API key",
                    "parameters": "News generation parameters",
                    "mode": "Generation mode",
                    "preview": "Preview",
                },
                "button": {
                    "generate": "Generate news for all stocks",
                },
                "input": {
                    "key": "Enter your Groq API key",
                    "key-placeholder": "Loaded from .env — type here to override",
                    "alpha": "Indicate the alpha value : The alpha parameter is a percentage of variation between two days.",
                    "alpha-day-interval": "Indicate the alpha day interval : The alpha day interval is the interval between the two days used for the calculation of alpha.",
                    "delta": "Indicate the delta value : The delta value shifts the news days by a certain number of days.",
                    "nbr-positive-news": "Number of positive news",
                    "nbr-negative-news": "Number of negative news",
                },
                "select": {
                    "ticker": "Select a stock",
                },
                "radio": {
                    "label": "Generation mode",
                    "options": ["Random mode", "Linear mode"],
                },
            },

            "revenues": {
                "subtitles": {
                    "ticker": "Stocks choice",
                    "preview": "Preview",
                    "mode": "Mode choice",
                    "modal": "Assign revenues",
                    "form": "Form",
                },
                "button": {
                    "modify": "Modify",
                    "delete": "Delete",
                    "select-all": "Select all",
                    "confirm": "Confirm",
                },
                "select": {
                    "ticker": "Select a stock",
                    "revenue": "Select a revenue",
                    "net-income": "Select a net income",
                },
                "radio": {
                    "label": "Mode choice",
                    "options": ["auto", "manual"],
                },
            },
            "advanced": {
                "subtitles": {
                    "init": "Initialization",
                },
                "button": {
                    "update": "Update",
                },
                "input": {
                    "update-time": "Time between updates (ms)",
                    "requests": "Max requests",
                    "cashflow": "Initial cashflow",
                },
            },
        },

    }
}