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

        # Settings Page
        "settings-title": "Paramètres",
        "settings-subtitles": {
            "market-data": "Paramètrage des données de marché",
            "charts-trends": "Tendances des graphiques",
            "charts-patterns": "Choix de l'action",
            "final-charts": "Prévisualisation",
            "generate-modal": "Générer des données de marché",
            "api": "Clé api Groq",
            "news-generation-param": "Paramètres de génération des actualités",
            "advanced-init": "Initialisation"
        },
        "settings-sliders": {
            "alpha": "Sélectionner la valeur d'alpha",
            "length": "Sélectionner la longueur d'un mouvement de marché"
        },
        "settings-radio": {
            "trend": "Sélectionner la tendance",
            "options": ["Hausse 📈", "Baisse 📉", "Stable"]
        },
        "settings-button": {
            "modify": "Modifier",
            "select-all": "Tout sélectionner",
            "add": "Ajouter",
            "confirm": "Valider",
            "update": "Mettre à jour",
            "generate": "Générer les news",
        },
        "settings-number-inputs": {
            "number-trends": "Nombre de tendances",
            "number-patterns": "Sélectionner un action"
        },
        "settings-timeline": "mouvement du marché",
        "settings-stocks-input": {
            "company": "Entreprise",
            "ticker": "Mnémonique",
            "activity": "Catégorie"
        },
        "settings-api" : "Clé API",
        "news-settings": {
            "alpha": "Alpha : Le paramètre alpha est un pourcentage de variation entre deux jours.",
            "alpha-day-interval": "Intervalle de jours alpha : L'intervalle de jours alpha est l'intervalle entre les deux jours utilisés pour le calcul de l'alpha.",
            "delta": "Delta : La valeur delta décale les jours de nouvelles de quelques jours.",
            "mode": "Mode de génération des actualités",
            "linear-mode": "Mode de génération linéaire",
            "random-mode": "Mode de génération aléatoire",
            "nbr-positive-news": "Nombre d'actualités positives",
            "nbr-negative-news" : "Nombre d'actualités négatives",
        },
        "settings-advanced-init-input": {
            "update-time": "Temps pour une journée (ms)",
            "requests": "Requêtes max",
            "cashflow": "Trésorie initiale"
        },
        "settings-tabs": {
            "stock": "Actions",
            "chart": "Graphiques",
            "news": "Actualités",
            "advanced": "Avancé"
        },
    },
}