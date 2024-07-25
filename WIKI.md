
## Wiki
- [Market](#market)
- [News](#news)
- [Revenues](#revenues)
- [Companies](#companies)
- [Import](#import-)
- [Export](#export)


# Market
Les données de marché peuvent être configurées pour chaque ticker. dans la section "Graphiques" de la page de configuration.

## Initialization
Quand vous lancerez l'application, les données de marché seront scrappé a l'aide de yahooquery et de yfinance.
Ce sont des données de marché réelles.

## Storage

### Path
Les données de marché sont stockées dans un fichier CSV.
Voici le chemin du fichier : `data/generated_data.csv`

### Format 
Les données sauvegardées pour chaque ticker sont les suivantes :
- `Open` : Le prix d'ouverture
- `High` : Le prix le plus haut
- `Low` : Le prix le plus bas
- `Close` : Le prix de fermeture
- `Volume` : Le volume de la journée
- `adjclose` : Le prix ajusté en fonction des dividendes et des splits
- `long_MA` : La moyenne mobile long terme
- `short_MA` : La moyenne mobile court terme
- `200_MA` : La moyenne mobile sur 200 jours

#### Index
- `date` : La date de la donnée

#### Columns
- `symbol` : Le ticker de l'entreprise
- `None` : Les colonnes de données (Open, High, Low, Close, Volume, adjclose, long_MA, short_MA, 200_MA)

#### Example
```csv
symbol,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,SAN.PA,^GSPC,^DJI,^FCHI,^SPGSGC,OR.PA,OR.PA,OR.PA,SAN.PA,SAN.PA,SAN.PA,^GSPC,^GSPC,^GSPC,^DJI,^DJI,^DJI,^FCHI,^FCHI,^FCHI,^SPGSGC,^SPGSGC,^SPGSGC
,Open,Open,Open,Open,Open,Open,High,High,High,High,High,High,Low,Low,Low,Low,Low,Low,Close,Close,Close,Close,Close,Close,Volume,Volume,Volume,Volume,Volume,Volume,adjclose,adjclose,adjclose,adjclose,adjclose,adjclose,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA,long_MA,short_MA,200_MA
date,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2023-02-03 01:00:00+01:00,375.5,84.75,4136.68994140625,33926.30078125,7136.39990234375,0.0,384.3999938964844,86.33999633789062,4182.35986328125,34179.578125,7233.93994140625,0.0,373.8999938964844,82.25,4123.35986328125,33813.859375,7113.419921875,0.0,384.3999938964844,85.13999938964844,4136.47998046875,33926.01171875,7233.93994140625,0.0,535365.0,4394526.0,4694510000.0,425150000.0,89988400.0,0.0,368.0873718261719,78.80525970458984,4136.47998046875,33926.01171875,7233.93994140625,0.0,379.83499908447266,359.2560003662109,346.90124923706054,89.86800079345703,90.16340087890624,86.64570022583008,4029.480029296875,3932.3714306640622,3932.8894165039064,33792.555078125,33511.6903125,32495.514296875,7066.147534179688,6816.817626953125,6433.342590332031,0.0,0.0,0.0
```

## Reset
Vous pouvez réinitialiser les données de marché en coupant l'application et en supprimant le fichier `data/generated_data.csv`
> **TODO** :
> Ajouter un bouton de réinitialisation dans l'interface

## Generation
Market data is generated for each company according to the selected trend (Bull, Bear, Flat). The algorithm searches randomly in the CAC40 market data for trends that match the selected parameters.
### Parameters
- `Charts trends` : Select the number of trends you want to generate and their shape (Bull, Bear, or Flat).
- `Alpha` : The minimum percentage value of market change between the first and last day.
- `Length` : The number of days for the generated trend.
- `Start value` : The start value for the generated data.




# News

## Initialization
Les news des données de marché réel ont été scrappé à l'avance et son contenu dans un .csv 

## Storage

### Path
Les données de news sont stockées dans un fichier CSV. 
Voici le chemin du fichier : `data/news.csv`

### Format
Les données sauvegardées pour chaque ticker sont les suivantes :
- `date` : La date de la donnée
- `ticker` : Le ticker de l'entreprise
- `title` : Le titre de l'article
- `content` : Le contenu de l'article
- `sector` : Le secteur de l'entreprise (Uniquement si la news est générée)
- `sentiment` : Le sentiment de l'article (Uniquement si la news est générée)

#### Columns
les colonnes du fichier sont celles decrites ci-dessus

#### Example
```csv
date;ticker;sector;title;content;sentiment
02/07/23 02:00;LVMH MOËT HENNESSY LOUIS VUITTON SE (MC);Textile Habillement Accessoires;LVMH : L'objectif de cours relevé à 740 E, une hausse de 14% attendue en 2024 !;UBS confirme son conseil à l'achat sur la valeur et relève son objectif de cours à 740 E (au lieu de 670 E) ce qui représente un potentiel de hausse de 14%. Nous nous attendons à ce que LVMH enregistre un bon début d'année 2024 avec une croissance des ventes et une dynamique continue en Asie, malgré les inquiétudes persistantes en Chine, défiant ainsi le contexte complexe du secteur. À moyen terme, en dépit des incertitudes économiques, géopolitiques et monétaires dans le monde, LVMH confirme un objectif de progression du chiffre d'affaires à taux constants ambitieux, et affirme 'aborder l'année 2024 avec confiance'.;positive
```

## Generation
News articles are generated using Llama3 and a dataset of news articles scraped from abcbourse.com. The LLM takes a news article from the same activity sector as the company in the dataset and reformulates it. The news will then be displayed either randomly or sequentially, depending on the selected mode, when a variation meets the specified parameters (alpha & alpha interval).

### Parameters
- `API key` : Enter your Groq API key for news generation.
- `Alpha` : The minimum percentage of market variation between two days required to display a news article.
- `Alpha interval` : The interval of days used to calculate the alpha variation.
- `Delta` : This value shifts the news by a certain number of days. For example, setting this to 1 will display the news one day earlier.

Each company is assigned to a sector of activity. The news generated will be from the same sector as the company.
> **WARNING** :
> We get the activity of the company from the `activities` store (defined in `defaults.py`).

> **TODO** :
> Switch the logic to use the `activity` field of `companies_list` instead.


# Revenues

## Initialization
Quand vous lancerez l'application, les revenus seront scrappé a l'aide de yahooquery et de yfinance.
Ces données sont réelles.

## Storage

### Path
Les données de marché sont stockées dans un fichier CSV.
Voici le chemin du fichier : `data/revenues.csv`

### Format

Les données sauvegardées pour chaque ticker sont les suivantes :
- `currencyCode`: la devise
- `NetIncome`:
- `TotalRevenue`: 
- `asOfDate`: l'année de la donnée 
- `symbol`: le ticker 

#### Index 
- `currencyCode` : la devise
- `NetIncome` :
- `TotalRevenue` :

#### Columns
- `symbol` : le ticker
- `asOfDate` : la date de la donnée 

#### Example 
```csv
symbol,ACA.PA,ACA.PA,ACA.PA,ACA.PA,AI.PA,AI.PA,AI.PA,AI.PA,AIR.PA,AIR.PA,AIR.PA,AIR.PA,BN.PA,BN.PA,BN.PA,BN.PA,BNP.PA,BNP.PA,BNP.PA,BNP.PA,CS.PA,CS.PA,CS.PA,CS.PA,DG.PA,DG.PA,DG.PA,DG.PA,DSY.PA,DSY.PA,DSY.PA,DSY.PA,EL.PA,EL.PA,EL.PA,EL.PA,KER.PA,KER.PA,KER.PA,KER.PA,MC.PA,MC.PA,MC.PA,MC.PA,OR.PA,OR.PA,OR.PA,OR.PA,RI.PA,RI.PA,RI.PA,RI.PA,RMS.PA,RMS.PA,RMS.PA,RMS.PA,SAF.PA,SAF.PA,SAF.PA,SAF.PA,SAN.PA,SAN.PA,SAN.PA,SAN.PA,STLAM.MI,STLAM.MI,STLAM.MI,STLAM.MI,STMPA.PA,STMPA.PA,STMPA.PA,STMPA.PA,SU.PA,SU.PA,SU.PA,SU.PA,TTE.PA,TTE.PA,TTE.PA,TTE.PA
asOfDate,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2019-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-06-30 00:00:00,2021-06-30 00:00:00,2022-06-30 00:00:00,2023-06-30 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00,2020-12-31 00:00:00,2021-12-31 00:00:00,2022-12-31 00:00:00,2023-12-31 00:00:00
currencyCode,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,EUR,USD,USD,USD,USD,EUR,EUR,EUR,EUR,USD,USD,USD,USD
NetIncome,2692000000.0,5844000000.0,5306000000.0,6348000000.0,2435100000.0,2572200000.0,2758800000.0,3078000000.0,-1133000000.0,4213000000.0,4247000000.0,3789000000.0,1956000000.0,1924000000.0,959000000.0,881000000.0,7067000000.0,9488000000.0,9848000000.0,10975000000.0,3857000000.0,3164000000.0,7294000000.0,6675000000.0,1242000000.0,2597000000.0,4259000000.0,4702000000.0,491000000.0,773700000.0,931500000.0,1050900000.0,85000000.0,1448000000.0,2152000000.0,2289000000.0,2150400000.0,3176000000.0,3614000000.0,2983000000.0,4702000000.0,12036000000.0,14084000000.0,15174000000.0,3563400000.0,4597100000.0,5706600000.0,6184000000.0,329000000.0,1305000000.0,1996000000.0,2262000000.0,1385000000.0,2445000000.0,3367000000.0,4311000000.0,352000000.0,43000000.0,-2459000000.0,3444000000.0,12294000000.0,6223000000.0,8371000000.0,5400000000.0,2173000000.0,14200000000.0,16799000000.0,18596000000.0,1106000000.0,2000000000.0,3960000000.0,4211000000.0,2126000000.0,3204000000.0,3477000000.0,4003000000.0,-7242000000.0,16032000000.0,20526000000.0,21384000000.0
TotalRevenue,18015000000.0,21397000000.0,20646000000.0,23455000000.0,20485200000.0,23334800000.0,29934000000.0,27607600000.0,49912000000.0,52149000000.0,58763000000.0,65446000000.0,23620000000.0,24281000000.0,27661000000.0,27619000000.0,52285000000.0,56355000000.0,57477000000.0,59735000000.0,124942000000.0,102897000000.0,111692000000.0,93083000000.0,44118000000.0,50230000000.0,62514000000.0,69885000000.0,4452200000.0,4860100000.0,5665200000.0,5951400000.0,14429000000.0,19820000000.0,24494000000.0,25395000000.0,13100200000.0,17645000000.0,20351000000.0,19566000000.0,44651000000.0,64215000000.0,79183000000.0,86153000000.0,27992100000.0,32287600000.0,38260600000.0,41182500000.0,8448000000.0,8824000000.0,10701000000.0,12137000000.0,6389000000.0,8981000000.0,11601000000.0,13427000000.0,16631000000.0,15133000000.0,19523000000.0,23651000000.0,37369000000.0,39175000000.0,45389000000.0,46444000000.0,47656000000.0,149419000000.0,179592000000.0,189544000000.0,10219000000.0,12761000000.0,16128000000.0,17286000000.0,25159000000.0,28905000000.0,34176000000.0,35902000000.0,119704000000.0,184634000000.0,263310000000.0,218945000000.0
```

## Generation

Les données ne sont pas réelement génerées. Elles sont peuvent être scrappée ou definies à la main.

### Scrapping
On utilise yahooquery pour récuperer les revenus du/des tickers entre 2020 et la dernière année definies dans le csv des données de marché (`data/generated_data.csv`)

> **WARNING** :
Si le ticker n'existe pas dans le monde réel, cela ne marchera pas

### Manual 
Vous pouvez rentrer les données manuellement sur l'interface


# Companies

## Initialization
Une liste d'entreprise et d'indexes sont definis initialement dans le fichier `defaults.py`

Les données de ces tickers seront scrappé a l'aide de yahooquery et de yfinance.
Vous pouvez ajouter/enlever des entreprises dans le fichier `defaults.py` avant le lancement de l'application pour scrapper leurs données de marché réelles.

> **WARNING** :
> Si vous ajoutez des entreprises après le lancement de l'application, vous devrez les ajouter manuellement dans la page de configuration.

> **WARNING** :
> Si vous mettez des entreprises qui n'existent pas dans le monde réel, les données de marché ne pourront pas être scrappées. Cela engendrera une erreur.

> **WARNING** :
> Actuellement le champ `activity` n'est pas utilisé pour la géneration de news dans companies_list.

## Storage
### Path
Les données des entreprises / indices sont stockées dans un element Store de Dash. (dcc.Store)
Les données sont ainsi stockée dans le navigateur du client de maniere locale.

### Format
Les données sont stockées dans un dictionnaire avec les clés suivantes :
- `label` : Le nom de l'entreprise ou de l'indice
- `got_charts` : Si les données de marché ont été assignées (boolean)
- `activity` : Le secteur d'activité de l'entreprise ou "Indice" si c'est un indice

La clé de chaque dictionnaire correspond au Ticker.

#### Example
```python
companies = {
        "MC.PA": {
            "label": "LVMH MOËT HENNESSY LOUIS VUITTON SE (MC)",
            "activity": "Textile Habillement Accessoires",
            "got_charts": False,
        },
        "OR.PA": {
            "label": "L'ORÉAL (OR)",
            "activity": "Chimie Pharmacie Cosmétiques",
            "got_charts": False,
        },
         "^GSPC": {
            "label": "S&P 500",
            "activity": "Indice",
            "got_charts": True,
        },
    }
```


Vous pouvez aussi en créer dans la page de configuration en remplissant les champs:
- `Entreprise`
- `Ticker`
- `Secteur`

Une fois ceci fait, vous pouvez générer les données de marché et les revenus pour chaque Ticker.

> **WARNING** :
Si vous n'avez pas assigné de données de marché au ticker, vous ne pourrez pas generer les revenus ni les news.
Ainsi, ce Ticker ne sera pas intégré dans la simulation.

# Import 

Vous pouvez importer des données de marché, des revenus et des news en important des fichiers CSV formaté dans le bon format :
- [Market](#format-)
- [News](#format)
- [Revenues](#format-1)

> **WARNING** :
Pour importer proprement vos données, veuillez utiliser l'onglet `Import` de la page de configuration

#### Example
Importer les données de marché à travers cette page, permet de mettre à jour le champ `got_charts` du Store companies (cf [Companies](#format-2)).

# Export
All the data used and generated are stored. We export the information of the interactions with the application, the portfolio and the requests. 

## Storage

### Path
Les données exportés sont stockées dans 3 fichiers CSV.
Il y a 3 fichiers par session : 
- `interface-logs.csv` : Les logs de l'interface
- `portfolio-logs.csv` : Les logs du portefeuille
- `request-logs.csv` : Les logs des requêtes

Chaque ligne de chaque CSV contient un UUID permettant de relier les logs entre eux.

#### During the simulation
Lorsque la simulation est en cours, les données sont stockées dans le dossier `data/export`

#### After the simulation
Une fois la simulation terminée, les données sont stockées dans le dossier `data/exports`
Chaque session a son propre dossier et un ID unique.
L'ID des sessions est incrémenté à chaque nouvelle session.

### Triggers
Les données sont exportées à chaque fois qu'une action est effectuée par l'utilisateur.
- Lorsqu'une news est cliquée ou fermée
- Lorsqu'une action est effectuée sur le formulaire de requêtes (changement de type d'action)
- Lors d'un changement de type de graphique (Données de marché ou Revenus)
- Lorsque le ticker selectionné change
- Lorsqu'une requête est ajoutée
- Lorsqu'une requête est supprimée
- Lorsqu'une action est effectuée sur le portefeuille (Achat ou Vente)
- Lorsque le timestamp de la donnée de marché change

### interface-logs.csv 
Les données sauvegardées sont les suivantes :
- `uuid` : L'identifiant unique de la session (trigger)
- `market-timestamp` : Le timestamp de la donnée de marché (la date de la simulation)
- `host-timestamp` : Le timestamp de l'interaction (la date réele)
- `cashflow` : Le cashflow de l'utilisateur
- `selected-company` : L'entreprise sélectionnée
- `form-action` : L'état du formulaire de requetes (Achat ou Vente)
- `chart-type` : Le type de graphique sélectionné (Données de marché ou Revenus)
- `is_news_description_displayed` : (bool) Si une news a été cliqué pour afficher la description
- `news_title` : Le titre de la news cliqué ou None

#### Example
```csv
uuid,market-timestamp,host-timestamp,cashflow,selected-company,form-action,chart-type,is_news_description_displayed,news_title
6ab4129b-1d72-410b-bed8-6e001bed8a85,2005-04-30T00:00:00,1721135847.22061,100000,OR.PA,sell,market,False,
```

### portfolio-logs.csv
Les données sauvegardées sont les suivantes :
- `uuid` : L'identifiant unique de la session (trigger)
- `[Ticker]-shares` : Le nombre d'actions du ticker
- `[Ticker]-totals` : La valeur totale des actions du ticker

#### Example
```csv
uuid,MC.PA-shares,OR.PA-shares,RMS.PA-shares,TTE.PA-shares,SAN.PA-shares,AIR.PA-shares,SU.PA-shares,AI.PA-shares,EL.PA-shares,BNP.PA-shares,KER.PA-shares,DG.PA-shares,CS.PA-shares,SAF.PA-shares,RI.PA-shares,DSY.PA-shares,STLAM.MI-shares,BN.PA-shares,STMPA.PA-shares,ACA.PA-shares,^GSPC-shares,^DJI-shares,^FCHI-shares,^SPGSGC-shares,MC.PA-totals,OR.PA-totals,RMS.PA-totals,TTE.PA-totals,SAN.PA-totals,AIR.PA-totals,SU.PA-totals,AI.PA-totals,EL.PA-totals,BNP.PA-totals,KER.PA-totals,DG.PA-totals,CS.PA-totals,SAF.PA-totals,RI.PA-totals,DSY.PA-totals,STLAM.MI-totals,BN.PA-totals,STMPA.PA-totals,ACA.PA-totals,^GSPC-totals,^DJI-totals,^FCHI-totals,^SPGSGC-totals
8ae40745-8d76-4cd8-b3f3-c2b8d229e7fb,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

### request-logs.csv
Les données sauvegardées sont les suivantes :
- uuid : L'identifiant unique de la ligne (trigger)
- deleted-request : les index des requêtes supprimées
- request-[n] : Les requêtes de l'utilisateur : [action] [price] [quantity] [ticker]

#### Example
```csv
uuid,deleted-request,request-1,request-2,request-3,request-4,request-5,request-6,request-7,request-8,request-9,request-10
62cffea7-2113-498f-aef9-fa6963640406,[0],buy 1000 1 MC.PA,buy 1000 1 MC.PA,buy 1000 1 MC.PA,,,,,,,
```

