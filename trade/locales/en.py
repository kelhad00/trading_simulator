translation = {
    'en': {
        # Portfolio
        "portfolio": "Portfolio",
        'portfolio-columns': {'Stock': 'Stocks', 'Shares': 'Shares', 'Total': 'Price'},
        "portfolio-cashflow": "Cashflow: ",
        "portfolio-investment": "Total investment: ",

        # Company graph
        "price": "Price",
        "tab-market": "Technical Analysis",
        "tab-revenue": "Revenue",
        "interval": "Time unit",
        "interval-hour": "Hour",
        "interval-day": "Day",
        "interval-week": "Week",
        "interval-month": "Month",
        "market-graph": {
            'x': 'Date',
            'y': 'Price',
            'legend': {
                'longMA': ' Simple moving average (20)',
                'shortMA': ' Simple moving average (50)',
                'twohunMA': ' Simple moving average (200)', 
                'price': 'Price',
                'RSI': 'RSI',
                'upper zone': 'Over-buy zone',
                'lower zone': 'Over-sell zone',
                'upper-limit': 'Upper limit',
                'lower-limit': 'Lower limit',
            },
        },
        "revenue-graph": {
            "totalRevenue": "Revenue",
            "netIncome": "Net Income"
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
                "pattern": "Pattern",
            },
            "charts": {
                "subtitles": {
                    "modal": "Market data creation",
                    "ticker": "Stock choice",
                    "companies": "Companies",
                    "preview": "Preview",
                    "parameters": "Market movement parameters",
                    "trends": "Charts trends",
                    "Old generator":"Preview",
                    "New generator":"Generator",
                    "pattern_title": "Pattern",
                    'Very Bull':'Very Bull',
                    'Medium Bull':'Medium Bull',
                    'Small Bull':'Small Bull',
                    'Flat':'Flat',
                    'Small Bear':'Small Bear',
                    'Medium Bear':'Medium Bear',
                    'Very Bear':'Very Bear',
                    "preview_pattern_title": "Preview :",
                    "preview_pattern_day": "Day",
                    "preview_pattern_price": "Price",
                    "alert_select_pattern": "Please select a pattern.",
                    "alert_config_saved": "Configuration saved!",
                    "pattern_config": "Configure a custom pattern",
                    "pattern_preview": "Pattern preview",
                    "with_pattern": "With pattern",
                    "without_pattern" : "Without pattern",
                    "duration":"Duration",
                    "add_pattern":"Add pattern",
                },
                "button": {
                    "refresh":"Refresh the preview",
                    "modify": "Save changes",
                    "delete": "Delete",
                    "select-all": "Select all",
                    "select-unconfigured": "Select unconfigured",
                    "save_company_config": "Save configuration",
                    'Very Bull':'Add Very Bull',
                    'Medium Bull':'Add Medium Bull',
                    'Small Bull':'Add Small Bull',
                    'Flat':'Add Flat',
                    'Small Bear':'Add Small Bear',
                    'Medium Bear':'Add Medium Bear',
                    'Very Bear':'Add Very Bear',
                    "save_pattern_config": "Save configuration",
                    "reset_pattern_config": "Reset parameters",
                    "add_pattern": "Add pattern",
                },
                "table": {
                    "configured": "Configured",
                    "not_configured": "Not configured",
                    "ticker": "Ticker",
                    "status": "Status",
                    "no_company": "No company",
                    "no_trends": "No configured trend",
                    "trends_prefix": "Trends: "
                },
                "select": {
                    "ticker": "Select a stock",
                    "alpha": "Select alpha value",
                    "length": "Select length of a market movement",
                    "start": "Select start date",
                    "pattern": "Choose a pattern",
                    "date_range": "Generation period:",
                    "start_date": "Start date",
                    "end_date": "End date",
                    "granularity": "Granularity:",
                    "month": "Month",
                    "week": "Week",
                    "day": "Day",
                    "hour": "Hour",
                },
                "radio": {
                    "title": "market movement",
                    "label": "Select a trend",
                    "options": ["Bull 📈", "Bear 📉"],
                },
                "input": {
                    "trends": "Number of charts trends",
                },
                "patterns_params": {
                    "bullish_engulfing": {
                        "down1": "Day 1 drop (%)",
                        "up1": "Day 2 rise (%)"
                    },
                    "bearish_engulfing": {
                        "down1": "Day 2 drop (%)",
                        "up1": "Day 1 rise (%)"
                    },
                    "hammer": {
                        "low": "Body min (%)",
                        "high": "Body max (%)"
                    },
                    "shooting_star": {
                        "low": "Body min (%)",
                        "high": "Body max (%)"
                    },
                    "double_top": {
                        "top_init": "Initial top (%)",
                        "creux_init": "Initial bottom (%)",
                        "rise1": "Rise 1 (%)",
                        "low4": "Low 4 (%)",
                        "high4": "High 4 (%)",
                        "close5": "Close 5 (%)"
                    },
                    "head_and_shoulders": {
                        "shoulder_rate": "Shoulder (%)",
                        "head_rate": "Head (%)",
                        "neckline_rate": "Neckline (%)",
                        "breaking_rate": "Breakout (%)"
                    }
                },
                "patterns_names": {
                    "bullish_engulfing": "Bullish Engulfing",
                    "bearish_engulfing": "Bearish Engulfing",
                    "hammer": "Hammer",
                    "shooting_star": "Shooting Star",
                    "double_top": "Double Top",
                    "head_and_shoulders": "Head and Shoulders",
                    "double_bottom" : "Double Bottom",
                    "inverse_head_and_shoulders":"Inversed Head and Shoulders"
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
                },
                "input": {
                    "company": "Company",
                    "ticker": "Ticker",
                    "activity": "Activity",
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
                "notification":{
                    "title_update":"Settings updated",
                    "message_update":"Settings updated !",
                    "title_error":"Error",
                    "message_error":"Please fill all the fields with numbers",
                },
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