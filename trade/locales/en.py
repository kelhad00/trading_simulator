translation = {
    'en': {
        # Chart right-click context menu
        "ctx-menu": {
            "buy":  "Buy here",
            "sell": "Sell here",
        },

        # Simulation end modal
        "simulation-end": {
            "title":           "Simulation ended!",
            "validate":        "Validate",
            "initial-capital": "Initial capital",
            "final-value":     "Final value",
            "pnl":             "PNL",
            "cash":            "Remaining cash",
            "stocks-value":    "Stocks value",
            "breakdown-title": "Portfolio breakdown",
            "col-company":     "Company",
            "col-quantity":    "Quantity",
            "col-value":       "Value",
            "no-position":     "No position held",
            "shares":          "share(s)",
        },

        # Portfolio
        "portfolio": "Portfolio",
        'portfolio-columns': {'Stock': 'Stocks', 'Shares': 'Shares', 'Total': 'Total', 'CurPrice': 'Cur. Price', 'BoughtAt': 'Bought At', 'SoldAt': 'Sold At', 'PnL': 'PnL'},
        "portfolio-cashflow": "Cashflow: ",
        "portfolio-investment": "Total investment: ",

        # Company graph
        "tab-market": "Technical Analysis",
        "tab-revenue": "Revenue",
        "market-graph": {
            'x': 'Date',
            'y': 'Price',
            'legend': {
                'longMA': ' Simple moving average (50)',
                'shortMA': ' Simple moving average (20)',
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
        "news-notif-view": "Read article",
        "news-description-view": "View chart",
        "news-published": "Published:",

        # Request form
        "request-title": "Make a Request",
        "request-action": {
            "label": "Action",
            # "choices": {'buy': 'Buy','sell': 'Sell'}
            "choices": [{
                "label": "Buy",
                "value": "buy"
            }, {
                "label": "Sell",
                "value": "sell"
            }]
        },
        "request-price": "Price",
        "market-price-btn": "Market Price",
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

        "mode-config": "Configurator",
        "mode-runtime": "Simulation",

        "session": {
            "export-button": "Export Session",
            "import-label": "Import Session",
            "import-hint": "Drop session.zip here or click to upload",
            "import-success": "Session loaded — you can now start the simulation.",
            "import-error": "Invalid session file. Please use a file exported from the configurator.",
            "session-loaded-prefix": "Loaded:",
            "session-remove": "Remove",
            "export-tooltip": "Please generate the data in settings before exporting.",
            "start-tooltip": "Please import a session exported from the configurator before starting.",
        },
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
                    "segment-length": "Segment length (bars)",
                    "bars": "bars",
                    "start": "Select starting price",
                },
                "radio": {
                    "title": "market movement",
                    "label": "Select a trend",
                    "options": ["Bull 📈", "Bear 📉", "Flat"],
                },
                "input": {
                    "trends": "Number of charts trends",
                },
                "event": {
                    "title": "Event overlay",
                    "type-label": "Event type",
                    "none": "None",
                    "crash": "Crash",
                    "rally": "Rally",
                    "position": "Position (%)",
                    "magnitude": "Magnitude (%)",
                    "overlap-warning": "The %s starts inside segment %d which contains a %s pattern. The pattern shape will be distorted — consider moving the event to a segment without a pattern.",
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
                "sim-window": {
                    "start": "Simulation start",
                    "end": "Simulation end",
                    "legend": "🟢 start · 🔴 end — ~%d of %d bars will be shown during the %d-minute session",
                    "legend-all": "🟢 start · 🔴 end — all %d bars fit within the %d-minute session",
                    "legend-short": "⚠️ only %d bars generated — the session will run out of data after ~%d of the %d configured minutes",
                },
                "bar-count": {
                    "year": "yr",
                    "years": "yrs",
                    "month": "mo",
                    "with-duration": "%d bars  (~%s of trading data)",
                    "under-month": "%d bars  (< 1 mo of trading data)",
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
                    "provider": "LLM Provider",
                    "key": "Ollama URL",
                    "parameters": "News generation parameters",
                    "mode": "Generation mode",
                    "preview": "Preview",
                    "notifications": "Notifications",
                },
                "notifications": {
                    "enabled-label": "Show news notifications",
                    "filter-label": "Show notifications for",
                    "filter-positive": "Positive news",
                    "filter-negative": "Negative news",
                    "filter-neutral": "Neutral news",
                    "offset-label": "Days before news appears (0 = same time)",
                },
                "button": {
                    "generate": "Generate news for all stocks",
                },
                "provider": {
                    "label": "Choose how to generate news",
                    "ollama": "Local (Ollama)",
                    "groq": "Groq (Cloud — free tier)",
                    "groq-note": "Groq offers ~14 400 free requests/day. Get your API key at console.groq.com",
                },
                "input": {
                    "key": "Enter the Ollama base URL",
                    "key-placeholder": "Loaded from .env — type here to override (e.g. http://localhost:11434/v1)",
                    "groq-key": "Groq API Key",
                    "groq-key-placeholder": "Loaded from .env — type here to override",
                    "alpha": "Indicate the alpha value : The alpha parameter is a percentage of variation between two days.",
                    "alpha-day-interval": "Indicate the alpha day interval : The alpha day interval is the interval between the two days used for the calculation of alpha.",
                    "delta": "Indicate the delta value : The delta value shifts the news days by a certain number of days.",
                    "nbr-positive-news": "Number of positive news",
                    "nbr-negative-news": "Number of negative news",
                    "top-k": "Top-K filter (linear mode only)",
                    "top-k-description": "Keep only the K news with the biggest price swings. Set to 0 to keep all positions above alpha.",
                },
                "select": {
                    "ticker": "Select a stock",
                },
                "radio": {
                    "label": "Generation mode",
                    "options": ["Random mode", "Linear mode", "Manual mode"],
                },
                "manual": {
                    "sentiment-label": "Place news as",
                    "sentiment-positive": "Positive",
                    "sentiment-negative": "Negative",
                    "hover-text-idle": "Hover over the chart, then click to place",
                    "hover-text-active": "Click to place as {sentiment} on {date}",
                    "counter": "{positive} positive, {negative} negative placed for this company",
                    "counter-empty": "No positions placed yet for this company",
                    "clear": "Clear this company",
                    "clear-notif-title": "Manual positions cleared",
                    "clear-notif-msg": "Manual positions for {company} have been cleared.",
                    "date-label": "Or pick a date manually",
                    "date-add": "Add",
                    "flagged-notice": "{count} company has manual positions — it will override auto-generation when generating.",
                    "flagged-notice-plural": "{count} companies have manual positions — they will override auto-generation when generating.",
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
                    "active": "Active companies",
                },
                "button": {
                    "update": "Update",
                },
                "input": {
                    "update-time": "Time between updates (ms)",
                    "requests": "Max requests",
                    "cashflow": "Initial cashflow",
                    "simulation-duration": "Session duration (minutes)",
                },
                "news-font": {
                    "label": "News article font size",
                    "small": "Small",
                    "medium": "Medium",
                    "large": "Large",
                },
                "active": {
                    "dropdown-label": "Add a company",
                    "dropdown-placeholder": "Select a company to add...",
                    "box-placeholder": "No companies selected.",
                    "count": "{n} / {total} active",
                    "error-title": "Cannot remove",
                    "error-msg": "At least one company must remain active.",
                },
            },
        },

    }
}