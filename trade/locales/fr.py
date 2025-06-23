translation = {
    'fr' : {
        # Portfolio
        "portfolio": "Portefeuille",
        'portfolio-columns': {'Stock': 'Actions', 'Shares': 'Parts', 'Total': 'Prix'},
        "portfolio-cashflow": "Trésorerie: ",
        "portfolio-investment": "Investissement total: ",

        # Company graph
        "price": "Prix",
        "tab-market": "Analyse Technique",
        "tab-revenue": "Revenus",
        "market-graph": {
            'x': 'Date',
            'y': 'Prix',
            'legend': {
                'longMA': 'Moyenne mobile simple (20)',
                'shortMA': 'Moyenne mobile simple (50)',
                'twohunMA': 'Moyenne mobile simple (200)',
                'price': 'Prix',
                'RSI': 'RSI',
                'upper zone': 'Zone de sur-achat',
                'lower zone': 'Zone de sur-vente',
                'upper-limit': 'Borne haute',
                'lower-limit': 'Borne basse',
            },
        },
        "revenue-graph": {
            "totalRevenue": "Chiffre d\'affaire",
            "netIncome": "Résultat net"
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

        "button-start": "Démarrer la simulation",
        "button-settings": "Paramètres",
        "button-restart-sim": "Réinitialiser",
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
                    "Old generator":"Ancien générateur",
                    "New generator":"Nouveau générateur",
                    'Very Bull': 'Très Bull',
                    'Medium Bull': 'Moyen Bull',
                    'Small Bull': 'Petit Bull',
                    'Flat': 'Flat',
                    'Small Bear': 'Petit Bear',
                    'Medium Bear': 'Moyen Bear',
                    'Very Bear': 'Très Bear',
                    "preview_pattern_title": "Aperçu :",
                    "preview_pattern_day": "Jour",
                    "preview_pattern_price": "Prix",
                    "alert_select_pattern": "Veuillez sélectionner un pattern.",
                    "alert_config_saved": "Configuration sauvegardée !",
                    "pattern_config": "Configurer un pattern personnalisé",
                    "pattern_preview": "Aperçu du pattern",
                },
                "button": {
                    "refresh":"Rafraichir",
                    "modify": "Modifier",
                    "delete": "Supprimer",
                    "select-all": "Tout sélectionner",
                    'Very Bull': 'Ajouter Très Bull',
                    'Medium Bull': 'Ajouter Moyen Bull',
                    'Small Bull': 'Ajouter Petit Bull',
                    'Flat': 'Ajouter Flat',
                    'Small Bear': 'Ajouter Petit Bear',
                    'Medium Bear': 'Ajouter Moyen Bear',
                    'Very Bear': 'Ajouter Très Bear',
                    "save_pattern_config": "Sauvegarder la configuration",
                    "reset_pattern_config": "Réinitialiser les paramètres"
                },
                "select": {
                    "ticker": "Sélectionner une action",
                    "alpha": "Sélectionner la valeur d'alpha",
                    "length": "Sélectionner la longueur d'un mouvement de marché",
                    "start": "Sélectionner la valeur de départ",
                    "pattern": "Choisir un pattern"
                },
                "radio": {
                    "title": "mouvemement de marché",
                    "label": "Choix de la tendance",
                    "options": ["Bull 📈", "Bear 📉"],
                },
                "input": {
                    "trends": "Nombre de tendances",
                },
                "patterns_params": {
                    "bullish_engulfing": {
                        "down1": "Baisse jour 1 (%)",
                        "up1": "Hausse jour 2 (%)"
                    },
                    "bearish_engulfing": {
                        "down1": "Baisse jour 2 (%)",
                        "up1": "Hausse jour 1 (%)"
                    },
                    "hammer": {
                        "low": "Corps min (%)",
                        "high": "Corps max (%)"
                    },
                    "shooting_star": {
                        "low": "Corps min (%)",
                        "high": "Corps max (%)"
                    },
                    "double_top": {
                        "top_init": "Sommet initial (%)",
                        "creux_init": "Creux initial (%)",
                        "rise1": "Hausse 1 (%)",
                        "low4": "Bas 4 (%)",
                        "high4": "Haut 4 (%)",
                        "close5": "Clôture 5 (%)"
                    },
                    "head_and_shoulders": {
                        "shoulder_rate": "Épaule (%)",
                        "head_rate": "Tête (%)",
                        "neckline_rate": "Ligne de cou (%)",
                        "breaking_rate": "Cassure (%)"
                    }
                },
                "patterns_names": {
                    "bullish_engulfing": "Avalement haussier",
                    "bearish_engulfing": "Avalement baissier",
                    "hammer": "Marteau",
                    "shooting_star": "Étoile filante",
                    "double_top": "Double sommet",
                    "head_and_shoulders": "Tête et épaules"
                },
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
                    "revenue": "Revenu",
                    "net-income": "Recettes",
                },
                "radio": {
                    "label": "Choix du mode",
                    "options": ["Mode automatique", "Mode manuel"],
                },
            },
            "advanced": {
                "notification":{
                    "title_update":"Paramètres mis à jour",
                    "message_update":"Paramètres mis à jour !",
                    "title_error":"Erreur",
                    "message_error":"Merci de remplir tous les champs avec des valeurs numériques",
                },
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