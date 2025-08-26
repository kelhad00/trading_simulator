## Wiki

* [Market](#market)
* [Generation](#generation)
* [News](#news)
* [Revenues](#revenues)
* [Companies](#companies)
* [Import](#import-)
* [Export](#export)

# Market

Les données de marché peuvent être configurées pour chaque ticker dans la section "Graphiques" de la page de configuration.

## Initialization

Quand vous lancez l'application, aucune donnée réelle n’est chargée automatiquement.
Les données doivent être générées (cf. [Generation](#generation)) ou importées (cf. [Import](#import-)).

## Storage

### Path

Les données de marché sont stockées dans un fichier CSV.
Voici le chemin du fichier : `data/generated_data.csv`

### Format

Les données sauvegardées pour chaque ticker sont les suivantes :

* `Open` : Le prix d'ouverture
* `High` : Le prix le plus haut
* `Low` : Le prix le plus bas
* `Close` : Le prix de fermeture
* `Volume` : Le volume de la journée
* `adjclose` : Le prix ajusté
* `long_MA` : La moyenne mobile long terme
* `short_MA` : La moyenne mobile court terme
* `200_MA` : La moyenne mobile sur 200 jours

#### Index

* `date` : La date de la donnée

#### Columns

* `symbol` : Le ticker de l'entreprise
* `None` : Les colonnes de données (Open, High, Low, Close, Volume, adjclose, long\_MA, short\_MA, 200\_MA)

#### Example

```csv
symbol,OR.PA,SAN.PA
,Open,High
date,,
2023-02-03 01:00:00+01:00,375.5,384.3
```

## Reset

Vous pouvez réinitialiser les données de marché en coupant l'application et en supprimant le fichier `data/generated_data.csv`.

# Generation

La génération des données de marché se fait **par blocs** directement sur une timeline.
Chaque bloc correspond à une tendance (Bull, Bear ou Flat) et peut être manipulé visuellement.

## Fonctionnalités réalisées

* **Ajout de blocs** : possibilité d’insérer un nouveau bloc avec une tendance choisie (Bull, Bear ou Flat).
* **Suppression de blocs** : un bloc peut être retiré de la timeline.
* **Redimensionnement** : la durée d’un bloc (Length) se règle en étirant ses poignées gauche/droite.
* **Configuration via modal** : certains blocs possèdent une fenêtre de configuration accessible par bouton.

## Paramètres disponibles par bloc

* **Trend** : Bull / Bear / Flat
* **Intensité** : Petit / Moyen / Très
* **Length** : nombre de jours du bloc en fonction de sa taille relative dans la timeline

## Patterns

Dans la configuration du bloc, il est possible de :

* Choisir le **type d’insertion** : avec pattern ou sans pattern
* Sélectionner des **patterns** à inclure
* Utiliser deux modes :

  * **Type** : simple sélection de patterns
  * **Type & quantité** : sélection des patterns avec la quantité souhaitée pour chacun

# News

## Initialization

Les news des données de marché réelles ont été stockées dans un `.csv`.

## Storage

### Path

Les données de news sont stockées dans un fichier CSV :
`data/news.csv`

### Format

* `date` : La date de la donnée
* `ticker` : Le ticker de l'entreprise
* `title` : Le titre de l'article
* `content` : Le contenu de l'article
* `sector` : Le secteur de l'entreprise (uniquement si générée)
* `sentiment` : Le sentiment de l'article (uniquement si générée)

#### Example

```csv
date;ticker;sector;title;content;sentiment
02/07/23 02:00;LVMH (MC);Textile Habillement Accessoires;LVMH : L'objectif relevé à 740 E;UBS confirme son conseil à l'achat...;positive
```

## Generation

Les articles de news sont générés à l'aide de **Llama3** et d’un dataset d’articles.
Le modèle reformule un article du même secteur que l’entreprise.
Les news peuvent être affichées de manière aléatoire ou séquentielle, selon le mode choisi.

### Parameters

* `API key` : Clé API Groq pour la génération de news
* `Alpha` : Variation minimale de marché entre le premier et le dernier jour
* `Alpha interval` : Intervalle de jours utilisé pour calculer la variation
* `Delta` : Décalage des news (par ex. `1` = affichage un jour plus tôt)
* `Mode` : Sélection du mode (Aléatoire ou Séquentiel)

# Revenues

## Initialization

Les revenus ne sont pas générés automatiquement.
Ils peuvent être ajoutés **manuellement** via l’interface ou **importés** depuis un CSV.

## Storage

### Path

Les données de revenus sont stockées dans :
`data/revenues.csv`

### Format

* `currencyCode` : devise
* `NetIncome` : revenu net
* `TotalRevenue` : revenu total
* `asOfDate` : année de la donnée
* `symbol` : ticker

#### Example

```csv
symbol,ACA.PA,AI.PA
asOfDate,2020-12-31,2021-12-31
currencyCode,EUR,EUR
NetIncome,2692000000.0,5844000000.0
TotalRevenue,18015000000.0,21397000000.0
```

## Generation

Les données peuvent être définies manuellement sur l'interface.

# Companies

## Initialization

Une liste d’entreprises et d’indices est définie initialement dans le fichier `defaults.py`.
Vous pouvez aussi en créer dans la page de configuration.

## Storage

Les données sont stockées dans un `dcc.Store` de Dash, côté client (navigateur).

### Format

* `label` : Nom de l’entreprise ou de l’indice
* `got_charts` : Booléen indiquant si des données de marché ont été assignées
* `activity` : Secteur d’activité (ou "Indice" pour un indice)

#### Example

```python
companies = {
    "MC.PA": {
        "label": "LVMH",
        "activity": "Textile Habillement Accessoires",
        "got_charts": False,
    },
    "OR.PA": {
        "label": "L'ORÉAL",
        "activity": "Chimie Pharmacie Cosmétiques",
        "got_charts": False,
    },
}
```

> **WARNING** : Si vous n’avez pas assigné de données de marché à un ticker, vous ne pourrez pas générer ses revenus ni ses news.

# Import

Vous pouvez importer des données de marché, de revenus et des news via des fichiers CSV formatés correctement.

# Export

Toutes les données utilisées et générées sont exportées.
Cela inclut les interactions avec l’application, le portefeuille et les requêtes.

Les données sont exportées sous forme de CSV :

* `interface-logs.csv`
* `portfolio-logs.csv`
* `request-logs.csv`

Chaque session est identifiée par un **UUID** unique.
