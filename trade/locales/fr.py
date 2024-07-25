translation = {
    'fr' : {
        # Portfolio
        "portfolio": "Portefeuille",
        'portfolio-columns': {'Stock': 'Actions', 'Shares': 'Parts', 'Total': 'Prix'},
        "portfolio-cashflow": "Trésorie",
        "portfolio-investment": "Investissement total",

        # Company graph
        "tab-market": "Analyse Technique",
        "tab-revenue": "Revenus",
        "market-graph": {
            'x': 'Date',
            'y': 'Prix',
            'legend': {
                'longMA': 'Moyenne mobile simple (20)',
                'shortMA': 'Moyenne mobile simple (50)',
                'twohunMA': 'Moyenne mobile simple (200)',
                'price': 'Prix'
            },
        },
        "revenue-graph": {
            "totalRevenue": "Chiffre d\'affaire",
            "netIncome": "Recettes"
        },

        # News table
        "news": "Actualités du Marché",
        "news-table": {
            "date": "Date",
            "article": "Article"
        },

        # News description
        "title-news-description": "Description de l\'article",
        "button-news-description": "Fermer",

        # Request form
        "request-title": "Requêtes",
        "request-action": {
            "label": "Action",
            # "choices": {'sell': 'Vendre', 'buy': 'Acheter'}
            "choices": [{
                "label": "Vendre",
                "value": "sell"
            }, {
                "label": "Acheter",
                "value": "buy"

            }]
        },
        "request-price": "Prix",
        "request-shares": "Nombre d'actions",
        "submit-request": "Soumettre",
        "err-too-many-requests": "Vous avez trop de requêtes en attente !",
        "err-wrong-form": "Veuillez entrer un prix valide !",
        "err-enough-money": "Vous n'avez pas assez d'argent !",
        "err-enough-shares": "Vous n'avez pas assez d'actions de {} !",

        # Requests list
        "requests-list-title": "Liste d'attente",
        "requests-table": {
            "actions": "Type",
            "shares": "Parts",
            "company": "Actions",
            "price": "Prix "
        },
        "clear-all-requests-button": "Supprimer tout",
        "clear-requests-button": "Supprimer",

        # Home Page
        # "welcome": "Bienvenue sur l\'trade-legacy TradeSim !",
        # "info_txt": "Pour commencer la session, cliquer sur 'Démarrer l’expérience'. L\'interface est disponible en anglais et français.",
        # "signature": "L\'équipe TradeSim",
        "button-start": "Démarrer la simulation",
        "button-settings": "Paramètres",
        "button-restart-sim": "Réinitialiser",
        # "button-start-info": "Veuillez patienter quelques instants...",
        "welcome": ["Bienvenue sur", "TradeSim"],
        "description": ["Cliquer sur ", "'Démarrer la simulation'", ", pour commencer la session. L\'interface est disponible en ", "anglais ", "et ", "français", "."],










        "settings": {
            "title": "Paramètres",
            "tabs": {
                "ticker": "Actions",
                "chart": "Graphiques",
                "news": "Actualités",
                "advanced": "Avancé",
                "revenues": "Revenus",
                "import": "Importation",
            },
            "charts": {
                "subtitles": {
                    "modal": "Générer des données de marché",
                    "ticker": "Choix de l'action",
                    "preview": "Prévisualisation",
                    "parameters": "Paramètres des données de marché",
                    "trends": "Tendances des graphiques",
                },
                "button": {
                    "modify": "Modifier",
                    "delete": "Supprimer",
                    "select-all": "Tout sélectionner",
                },
                "select": {
                    "ticker": "Sélectionner une action",
                    "alpha": "Sélectionner la valeur d'alpha",
                    "length": "Sélectionner la longueur d'un mouvement de marché",
                    "start": "Sélectionner la valeur de départ",
                },
                "radio": {
                    "title": "mouvemement de marché",
                    "label": "Choix de la tendance",
                    "options": ["Bull 📈", "Bear 📉", "Flat"],
                },
                "input": {
                    "trends": "Nombre de tendances",
                }
            },
            "tickers": {
                "subtitles": {
                    "form": "Ajouter une action",
                    "list": "Liste des actions",
                },
                "button": {
                    "add": "Ajouter",
                    "reset": "Réinitialiser",
                },
                "input": {
                    "company": "Entreprise",
                    "ticker": "Mnémonique",
                    "activity": "Catégorie",
                },
            },
            "news": {
                "subtitles": {
                    "key": "Clé API Groq",
                    "parameters": "Paramètres de génération",
                    "mode": "Mode de génération",
                    "preview": "Prévisualisation",
                },
                "button": {
                    "generate": "Générer pour toutes les actions",
                },
                "input": {
                    "key": "Clé API Groq",
                    "alpha": "Indiquer un pourcentage de variation de marché entre 2 jours",
                    "alpha-day-interval": "Indiquer l'intervalle de jours pour le calcul de l'alpha",
                    "delta": "Indiquer une valeur de décallage",
                    "nbr-positive-news": "Nombre d'actualités positives",
                    "nbr-negative-news": "Nombre d'actualités négatives",
                },
                "select": {
                    "ticker": "Sélectionner une action",
                },
                "radio": {
                    "label": "Mode de génération des actualités",
                    "options": ["Mode aléatoire", "Mode linéaire"],
                },
            },

            "revenues": {
                "subtitles": {
                    "ticker": "Choix de l'action",
                    "preview": "Prévisualisation",
                    "mode": "Choix du mode",
                    "modal": "Attribuer des revenus",
                    "form": "Formulaire",
                },
                "button": {
                    "modify": "Modifier",
                    "delete": "Supprimer",
                    "select-all": "Tout sélectionner",
                    "confirm": "Valider",
                },
                "select": {
                    "ticker": "Sélectionner une action",
                    "revenues": "Revenu",
                    "net-income": "Recettes",
                },
                "radio": {
                    "label": "Choix du mode",
                    "options": ["Mode automatique", "Mode manuel"],
                },
            },
            "advanced": {
                "subtitles": {
                    "init": "Initialisation",
                },
                "button": {
                    "update": "Mettre à jour",
                },
                "input": {
                    "update-time": "Temps pour une journée (ms)",
                    "requests": "Requêtes max",
                    "cashflow": "Trésorie initiale"
                },
            },
        },
    },
}