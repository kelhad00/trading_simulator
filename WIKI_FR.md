
## Wiki
- [Market](#market)
- [News](#news)
- [Revenues](#revenues)
- [Companies](#companies)
- [Paramètres et fonctionnalités](#paramètres-et-fonctionnalités)
- [Fichier de session (session.zip)](#fichier-de-session-sessionzip)
- [Import](#import-)
- [Export](#export)


# Market
Les données de marché peuvent être configurées pour chaque ticker. Dans la section "Graphiques" de la page de configuration.

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
Vous pouvez réinitialiser les données de marché en coupant l'application et en supprimant le fichier `data/generated_data.csv`,
ou générer de nouvelles données pour une entreprise dans Paramètres → Graphiques (« Modifier »).

Le bouton **Reset** du menu ne touche pas aux données de marché : il démarre une nouvelle session pour le
participant (argent de départ, aucun ordre ni action, nouveau dossier de logs). Voir [Export](#export).

## Generation
Les données de marché sont générées pour chaque entreprise en fonction de la tendance sélectionnée (Bull, Bear, Flat). L'algorithme recherche aléatoirement dans les données de marché du CAC40 des tendances qui correspondent aux paramètres sélectionnés.

### Parameters
- `Charts trends` : Sélectionnez le nombre de tendances que vous souhaitez générer et leur forme (Bull, Bear, ou Flat).
- `Alpha` : La valeur minimale de variation du marché entre le premier et le dernier jour.
- `Length` : Le nombre de jours pour la tendance générée.
- `Start value` : La valeur de départ pour les données générées.
- `Modèle technique (facultatif)` : une figure chartiste dessinée dans une tendance : Double Top,
  Double Bottom, Head & Shoulders, Inverse Head & Shoulders, Ascending / Descending Triangle,
  Bullish / Bearish Flag, Cup & Handle, Rising / Falling Wedge.
- `Superposition d'événement` : un **Crash** ou un **Rally** soudain ajouté par-dessus les tendances,
  avec sa `Position (%)` dans le graphique et son `Ampleur (%)`. Un avertissement apparaît si
  l'événement commence dans un segment qui contient une figure, car sa forme serait déformée.

Une fois les données de marché générées, les actualités de ces entreprises sont générées en arrière-plan
avec les réglages de l'onglet Actualités ; une notification indique quand c'est fini.

# News

## Initialization
Les news des données de marché réeles ont été scrappé à l'avance et son contenu dans un .csv 

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
- `sentiment` : Le ton demandé pour l'article, `positive` ou `negative` (Uniquement si la news est générée)
- `sentiment_label` : Le ton que FinBERT lit dans l'article : `strong positive`, `weak positive`,
  `neutral`, `weak negative` ou `strong negative`. Il décide de l'étiquette et de la couleur montrées
  au participant, et du filtre des notifications (Uniquement si la news est générée)

#### Columns
Les colonnes du fichier sont celles décrites ci-dessus, séparées par `;`.

#### Example
```csv
date;ticker;sector;title;content;sentiment
02/07/23 02:00;LVMH MOËT HENNESSY LOUIS VUITTON SE (MC);Textile Habillement Accessoires;LVMH : L'objectif de cours relevé à 740 E, une hausse de 14% attendue en 2024 !;UBS confirme son conseil à l'achat sur la valeur et relève son objectif de cours à 740 E (au lieu de 670 E) ce qui représente un potentiel de hausse de 14%. Nous nous attendons à ce que LVMH enregistre un bon début d'année 2024 avec une croissance des ventes et une dynamique continue en Asie, malgré les inquiétudes persistantes en Chine, défiant ainsi le contexte complexe du secteur. À moyen terme, en dépit des incertitudes économiques, géopolitiques et monétaires dans le monde, LVMH confirme un objectif de progression du chiffre d'affaires à taux constants ambitieux, et affirme 'aborder l'année 2024 avec confiance'.;positive
```

## Generation

Les articles sont écrits par un modèle d'IA, soit dans le cloud avec **Groq** (offre gratuite, clé
d'API nécessaire), soit sur l'ordinateur avec **Ollama**. Le modèle est réglé dans `.env`
(`GROQ_MODEL`, par défaut `openai/gpt-oss-120b` ; `OLLAMA_MODEL`, par défaut `qwen3:8b`). Chaque
article est placé là où le prix varie assez (alpha) et écrit pour correspondre à ce mouvement :
positif quand le prix monte, négatif quand il baisse. Chaque entreprise a un secteur d'activité,
utilisé dans l'article.

Chaque article est ensuite vérifié par **FinBERT**, un second modèle qui lit son ton (colonne
`sentiment_label`). Les résultats sont dans `data/verification_report.csv` ; sans les paquets de
FinBERT, les articles sont marqués `needs_review` (voir README, « Generating news »).

### Parameters
- `Choisir le mode de génération` : Local (Ollama) ou Groq (Cloud). L'URL d'Ollama et la clé d'API
  Groq sont lues dans `.env` ; écrire dans la case les remplace.
- `Alpha` : Le pourcentage minimal de variation du marché entre deux jours pour placer une actualité.
- `Alpha interval` : L'intervalle de jours utilisé pour calculer la variation alpha.
- `Delta` : Cette valeur décale les news de quelques jours. Par exemple, en la réglant à 1, les news seront affichées un jour plus tôt.

### Mode de génération
- `Mode aléatoire` : choisir combien d'actualités positives et négatives placer, au hasard parmi les
  mouvements au-dessus d'alpha.
- `Mode linéaire` : placer les actualités sur les mouvements au-dessus d'alpha, dans l'ordre. `Top-K`
  ne garde que les K plus grandes variations (0 = toutes).
- `Mode manuel` : cliquer sur le graphique (ou choisir une date) pour placer soi-même chaque actualité
  positive ou négative. Les entreprises avec des positions manuelles les utilisent à la place du
  placement automatique.

Chaque entreprise est assignée à un secteur d'activité. Les news générées seront du même secteur que l'entreprise.

# Revenues

## Initialization
Quand vous lancerez l'application, les revenus seront scrappé a l'aide de yahooquery et de yfinance.
Ces données sont réelles.

## Storage

### Path
Les données de revenus sont stockées dans un fichier CSV.
Voici le chemin du fichier : `data/revenue.csv`

Plusieurs entreprises peuvent être enregistrées en une fois dans Paramètres → Revenus (cela plantait avant le 30 oct. 2026).

### Format

Les données sauvegardées pour chaque ticker sont les suivantes :
- `currencyCode`: la devise
- `NetIncome`: le résultat net de l'entreprise (bénéfice après tous les coûts et impôts) pour l'année
- `TotalRevenue`: le chiffre d'affaires total de l'entreprise pour l'année
- `asOfDate`: la date de fin de l'exercice
- `symbol`: le ticker

Le participant les voit sous forme de graphique en barres (l'onglet revenus du graphique), seulement
pour les années terminées avant la date simulée en cours. Les indices n'ont pas de revenus.

#### Index 
- `currencyCode` : la devise
- `NetIncome` : le résultat net
- `TotalRevenue` : le chiffre d'affaires total

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
> Si vous mettez des entreprises qui n'existent pas dans le monde réel, les données de marché ne pourront pas être scrappées. Cela engendrera une erreur.

> **WARNING** :
> Si vous ajoutez des entreprises après le lancement de l'application, vous devrez les ajouter manuellement dans la page de configuration.

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




# Paramètres et fonctionnalités
Le chercheur les règle dans le Configurateur (`python app_config.py`, page Paramètres). Chaque
paramètre est enregistré dans le navigateur et transmis aux ordinateurs des participants par le
[fichier de session](#fichier-de-session-sessionzip). Les libellés ci-dessous sont ceux de l'interface en français.

Chaque fonctionnalité ajoutée pendant le stage de 2026 est **désactivée tant que le chercheur ne
l'active pas** (décision des encadrants, 30 oct. 2026) : bougies en mouvement, chemin aléatoire,
rappels de temps, classement, mode discret, frais de commission, boutons Autoscale / Reset axes du
graphique. Les notifications et les étiquettes des actualités, qui existaient avant, restent activées.

Ces valeurs par défaut valent pour un navigateur qui n'a jamais enregistré le paramètre. Un navigateur
qui en a déjà enregistré un garde sa valeur (le bouton **Réinitialiser** relance la simulation, pas les
paramètres) : le changer dans Paramètres, ou effacer les données du site pour l'application.

## Paramètres → Avancé

| Paramètre | Rôle | Par défaut |
|---|---|---|
| Trésorie initiale | Argent de départ du participant | 100 000 € |
| Requêtes max | Nombre maximum d'ordres en attente en même temps | 10 |
| Durée de la session (minutes) | Durée réelle de la session (mode chronomètre) | 15 |
| Temps entre deux mises à jour (ms), par étape de bougie | Temps entre deux mises à jour du graphique | 5000 |
| Bougies d'historique affichées au départ | Bougies passées visibles avant le début du trading | 100 |
| Frais de commission (%) | Payés à chaque achat et vente exécutés : avec 0,05, acheter 100 € coûte 100,05 €, vendre 100 € rapporte 99,95 € | 0 (sans frais) |
| Bougies en mouvement | La dernière bougie se forme par étapes (toutes les 30, 15 ou 5 min d'une bougie d'1 h) avant de se fermer, comme un graphique en direct. « Désactivé » = bougies affichées terminées | désactivé |
| Mouvement du prix dans une bougie en cours | Seulement avec les bougies en mouvement. **Simple** ou **Aléatoire**, voir [plus bas](#mouvement-du-prix-dans-une-bougie-en-cours) | Simple |
| Taille de police des articles | Petite / Moyenne / Grande | Petite |
| Entreprises actives | Entreprises que le participant peut trader (au moins une) | toutes celles avec des données de marché |
| Mode sombre pour la simulation | Thème sombre pour le participant | désactivé |
| Afficher le classement | Classement du participant contre 20 traders robots | désactivé |
| Afficher les boutons Autoscale et Reset axes sur le graphique | Les deux boutons décrits dans [Graphique du participant](#graphique-du-participant) | désactivé |

### Mouvement du prix dans une bougie en cours
Les données de marché n'ont que l'ouverture, le plus haut, le plus bas et la clôture finale de chaque
bougie : les prix entre les deux sont donc générés (`trade/utils/candle_steps.py`) :
- **Simple** : ouverture → plus bas → plus haut → clôture pour une bougie haussière (ouverture → plus
  haut → plus bas → clôture pour une bougie baissière), avec un peu de bruit.
- **Aléatoire** (ajouté après la réponse des encadrants, 30 oct. 2026) : le plus haut ou le plus bas peut
  venir en premier, et le prix varie librement entre eux (un « pont brownien » : une marche aléatoire
  dont le début et la fin sont fixés), comme une feuille qui dérive sur une rivière entre ses deux rives.

Les deux restent toujours dans la vraie bougie, atteignent son vrai plus haut et son vrai plus bas, et
finissent exactement à sa clôture. Le chemin est généré à partir d'une graine faite de l'entreprise et
de la date : tous les participants voient le même. Le graphique, le bouton « prix du marché », les
ordres en attente et le classement utilisent tous le chemin choisi.

### Classement
Les 20 robots sont créés à partir des prix de l'application : à la première bougie, chaque robot garde
5 à 40 % de l'argent de départ en liquide et achète un mélange aléatoire d'entreprises (en payant les
frais de commission), puis ne fait plus aucun ordre. Une graine fixe donne les mêmes robots à tous les
participants. Tout le monde est classé selon son total = liquide + argent mis de côté pour les ordres
d'achat en attente + valeur des actions. Avec les bougies en mouvement, les robots sont évalués au prix
atteint jusque-là dans la bougie en cours, comme le participant (`trade/utils/leaderboard.py`).

### Mode discret (essais)
Au lieu d'une horloge qui avance, le graphique s'arrête à des bougies fixées (« essais ») et le
participant passe à la suite avec le bouton **Essai suivant**. Désactivé par défaut.

- **Bougies affichées à chaque essai** : par exemple `10, 15` → l'essai 1 montre les bougies 1 à 10,
  l'essai 2 les bougies 1 à 15. Des nombres entiers, chacun plus grand que le précédent. L'enregistrement
  règle aussi « Bougies d'historique affichées au départ » sur le premier nombre.
- Les ordres en attente sont vérifiés sur chaque bougie sautée par un essai.
- Pas de chronomètre : la session se termine après le dernier essai.
- **Confirmation** : « Essai suivant » demande d'abord « Avez-vous fini d'acheter et de vendre pour cet
  essai ? Vous ne pourrez pas y revenir. » (« Non, rester » / « Oui, essai suivant ») ; au dernier essai,
  il demande de terminer la session.
- **Pas de notifications d'actualités** dans ce mode (un essai peut sauter beaucoup d'actualités d'un
  coup) ; les actualités restent dans la liste.
- **Zoomer sur les bougies tant qu'il y en a moins que** (100 par défaut) : tant que moins de bougies
  que ce nombre sont affichées, le graphique zoome sur elles ; à partir de ce nombre, il montre toute la
  largeur de la session. 0 = toujours toute la session.

## Paramètres → Actualités → Notifications

| Paramètre | Rôle | Par défaut |
|---|---|---|
| Afficher les notifications d'actualités | Pop-ups quand une actualité apparaît | activé |
| Afficher les notifications pour | Actualités positives / négatives / neutres | les trois |
| Jours avant l'apparition de l'actualité | Montre l'actualité ce nombre de jours avant sa date (0 = en même temps) | 0 |
| Afficher les rappels de temps | Pop-ups à 25 %, 50 %, 75 % de la session et à 5, 2 et 1 minutes de la fin | désactivé |
| Afficher les étiquettes et couleurs de sentiment | Étiquettes et couleurs positives/négatives dans la liste des actualités | activé |

## Graphique du participant
La barre d'outils au-dessus du graphique (zoom, déplacement, tracer une ligne, zoom avant/arrière) est
toujours affichée. Les deux boutons ci-dessous n'y sont que si **Afficher les boutons Autoscale et Reset
axes sur le graphique** est activé (Paramètres → Avancé, désactivé par défaut).
- **Autoscale** (bouton de la barre d'outils ou double-clic) : ajuste la vue aux bougies affichées, et
  continue de l'ajuster à chaque mise à jour.
- **Reset axes** (bouton de la barre d'outils) : revient à la vue de départ (toute la largeur de la
  session) et suit à nouveau le graphique en direct, aussi en pause ou après la fin.
- Un zoom ou un déplacement manuel reste là où le participant l'a laissé jusqu'à l'utilisation d'un de
  ces deux boutons. Changer d'entreprise revient toujours à la vue de départ.
- Code : `trade/callbacks/dashboard/graph.py` (`track_graph_auto_follow`).

## Fin de la session
Une fenêtre de résultats montre l'argent de départ, la valeur finale et le gain ou la perte. La valeur
finale compte le liquide, l'argent mis de côté pour les ordres d'achat encore en attente et la valeur des
actions : le même total que le portefeuille et le classement (`trade/callbacks/reset.py`).

## Écran « Mise à jour… » (Configurateur uniquement)
Quand le Configurateur travaille plus de 0,3 s, la fenêtre est couverte par un indicateur de chargement
et « Mise à jour… » (« Updating… » en anglais), pour que le chercheur ne clique pas pendant une mise à
jour, comme un écran de chargement dans un jeu. Il disparaît dès que la mise à jour est finie.
L'application des participants (Runtime) n'en a pas (`trade/app.py`, `_loading_overlay`).




# Fichier de session (session.zip)
Le chercheur prépare la session dans le Configurateur, puis clique sur **Exporter la session** en haut
de la page Paramètres (disponible dès que des données de marché existent). Sur l'ordinateur de chaque
participant, le Runtime (`python app_runtime.py`) importe ce fichier sur la page d'accueil ; le bouton
de démarrage reste désactivé tant qu'aucune session n'est importée.

Le zip contient :
- `session.json` : tous les paramètres ci-dessus (entreprises, argent de départ, requêtes max, temps
  de mise à jour, durée de la session, taille de police, thème, notifications activées, filtre et délai
  des notifications, bougies en mouvement, mouvement du prix dans une bougie, boutons du graphique, bougies d'historique, rappels, étiquettes des actualités,
  classement, frais de commission, mode discret, essais, zoom) ;
- les fichiers de données `generated_data.csv`, `news.csv` et `revenue.csv` (`trade/utils/session.py`,
  `DATA_FILES`).

Un ancien fichier de session sans un paramètre garde l'ancien comportement pour celui-ci (par exemple
pas de classement, pas de frais, pas de zoom en mode discret, mouvement du prix Simple, pas de boutons
du graphique).

Un test (`tests/test_session_zip.py`) vérifie que chaque paramètre enregistré par le Configurateur est
exporté et importé, pour qu'un nouveau paramètre ne puisse pas être oublié.




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
Toutes les données utilisées et générées sont conservées. On enregistre les interactions avec l'application, le portefeuille et les requêtes.

## Storage

### Path
Les données exportés sont stockées dans 3 fichiers CSV.
Il y a 3 fichiers par session : 
- `interface-logs.csv` : Les logs de l'interface
- `portfolio-logs.csv` : Les logs du portefeuille
- `request-logs.csv` : Les logs des requêtes

Chaque ligne de chaque CSV contient un UUID permettant de relier les logs entre eux.

#### Un dossier par session
Chaque session écrit ses logs directement dans son propre dossier, `data/exports/<id de session>/`,
par exemple `data/exports/2026-10-07_10-15_a3f9/` (date, heure et une petite partie aléatoire). Une
session reçoit son ID à l'ouverture du tableau de bord ; Reset ou l'import d'une session en démarre une
nouvelle. Chaque ligne de log a une colonne `session-id`, et `log-info.json` dans le dossier enregistre
l'ID de session, la version du code TradeSim et les paramètres. Ainsi les logs des participants ne se
mélangent jamais, même si Reset est oublié ou si plusieurs participants utilisent le même serveur.

Les anciennes sessions étaient d'abord écrites dans `data/export` puis déplacées dans un dossier
numéroté (`data/exports/1`, `2`, ...) au Reset ; ces dossiers sont gardés tels quels.

### Triggers
Une ligne est écrite dans chacun des trois fichiers à chaque action du participant
(`trade/callbacks/dashboard/export.py`) :
- Lorsqu'une actualité est ouverte ou fermée
- Lorsque le formulaire de requêtes passe d'Achat à Vente ou l'inverse
- Lorsque le graphique passe des données de marché aux revenus ou l'inverse
- Lorsque l'entreprise sélectionnée change
- Lorsque la liste des ordres en attente change : un ordre est ajouté, modifié, exécuté ou annulé
- Lorsqu'un ordre ou tous les ordres sont supprimés

Les trois lignes d'une même action ont le même `uuid` : elles peuvent être reliées.

Les événements de session sont aussi écrits dans `interface-logs.csv`, avec le nom de l'événement dans
la colonne `form-action` : `session-start`, `session-pause`, `session-resume`, `next-trial` (mode
discret) et `session-finish`.

Avec les bougies en mouvement, `market-timestamp` contient les minutes atteintes dans la bougie
(ex. 03:15), pas seulement la date de la bougie.

### interface-logs.csv
Les données sauvegardées sont les suivantes :
- `uuid` : L'identifiant unique de l'action
- `session-id` : La session (même nom que le dossier)
- `market-timestamp` : Le timestamp de la donnée de marché (la date de la simulation)
- `host-timestamp` : Le timestamp de l'interaction (la date réelle, en secondes depuis 1970)
- `cashflow` : Le liquide du participant
- `selected-company` : L'entreprise sélectionnée
- `form-action` : L'état du formulaire de requêtes (`buy` ou `sell`), ou un événement de session
- `chart-type` : Le graphique sélectionné (`market` ou `revenue`)
- `is_news_description_displayed` : (bool) Si une actualité a été cliquée pour afficher sa description
- `news_title` : Le titre de l'actualité cliquée, ou vide

#### Example
```csv
uuid,session-id,market-timestamp,host-timestamp,cashflow,selected-company,form-action,chart-type,is_news_description_displayed,news_title
6bcf94a5-a75e-4d98-8115-8eb1fb87b340,2026-10-29_22-30_1e98,2025-08-11 03:00:00+02:00,1793309455.129577,100000,MC.PA,buy,market,False,
```

### portfolio-logs.csv
Les données sauvegardées sont les suivantes :
- `uuid` : L'identifiant unique de l'action
- `session-id` : La session
- `[Ticker]-shares` : Le nombre d'actions du ticker
- `[Ticker]-totals` : La valeur totale des actions du ticker

#### Example
```csv
uuid,session-id,MC.PA-shares,OR.PA-shares,...,MC.PA-totals,OR.PA-totals,...
6bcf94a5-a75e-4d98-8115-8eb1fb87b340,2026-10-29_22-30_1e98,0,0,...,0,0,...
```

### request-logs.csv
Les données sauvegardées sont les suivantes :
- `uuid` : L'identifiant unique de l'action
- `session-id` : La session
- `deleted-request` : Les index des ordres supprimés (`["all"]` quand tous sont supprimés)
- `request-[n]` : Les ordres en attente : [action] [prix] [quantité] [ticker], une colonne par ordre jusqu'à « Requêtes max »

#### Example
```csv
uuid,session-id,deleted-request,request-1,request-2,request-3,request-4,request-5,request-6,request-7,request-8,request-9,request-10
62cffea7-2113-498f-aef9-fa6963640406,2026-10-29_22-30_1e98,[0],buy 1000 1 MC.PA,buy 1000 1 MC.PA,,,,,,,,
```

### log-info.json
Écrit dans le dossier de la session à chaque démarrage : l'ID de session, la version du format des
logs, et pour chaque démarrage l'heure, la version du code TradeSim (commit git) et tous les
paramètres utilisés. Il répond à la question « quels paramètres et quelle version ont produit ces
logs ? ».

### Quand les colonnes changent
Si les entreprises ou les paramètres changent pendant une session, le fichier de log est réécrit avec
toutes les colonnes, les anciennes lignes recevant des cases vides pour les nouvelles : aucune valeur
ne se retrouve sous le mauvais titre. Un fichier abîmé par une ancienne version n'est pas modifié et
les nouvelles lignes vont dans une nouvelle partie, par ex. `portfolio-logs-2.csv`
(`trade/utils/export.py`, `save_df`).
