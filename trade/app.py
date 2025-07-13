from dash import Dash, html, dcc, Input, Output
import dash
import dash_mantine_components as dmc

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from trade.defaults import defaults as dlt
from trade.utils.market import get_first_timestamp, get_market_dataframe
from trade.utils.news import get_news_dataframe
from trade.utils.download import download_market_data
from trade.utils.config import save_current_config

external_scripts = [
    {'src': 'https://cdn.tailwindcss.com'}
]

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_scripts=external_scripts
)

theme = {
    "defaultRadius": "md",
    "components": {
        "Paper": {
            "defaultProps": {
                "p": "xs",
                "withBorder": True,
            }
        }
    },
}

market_df = get_market_dataframe()
news_df = get_news_dataframe()

portfolio_value = {ticker: 0 for ticker in dlt.companies_list.keys()}

app.layout = dmc.MantineProvider([
    dmc.NotificationsProvider([
        html.Div(id="notifications"),

        dcc.Store(id='timestamp', data=get_first_timestamp(market_df, 100), storage_type="session"),
        dcc.Store(id='requests', data=[], storage_type="session"),
        dcc.Store(id='portfolio-shares', data=portfolio_value, storage_type="session"),
        dcc.Store(id='portfolio-totals', data=portfolio_value, storage_type="session"),
        dcc.Store(id='cashflow', data=dlt.initial_money, storage_type="session"),

        dcc.Store(id="companies", data=dlt.companies_list, storage_type="local"),
        dcc.Store(id="nb_export", data=len(os.listdir(os.path.join(dlt.data_path, "exports"))), storage_type="session"),
        #for new graph generation
        dcc.Store(id="new-graph-df", data={}, storage_type="session"),

        # Advanced settings
        dcc.Store(id="initial-cashflow", data=dlt.initial_money, storage_type="session"),
        dcc.Store(id="max-requests", data=dlt.max_requests, storage_type="session"),
        dcc.Store(id="update-time", data=dlt.update_time, storage_type="session"),


        dash.page_container
    ])
], theme=theme)

app.clientside_callback(
    """
    function(n_clicks, children) {
        // Initialiser l'objet pour stocker les tailles si ce n'est pas déjà fait
        if (!window.itemSizes) {
            window.itemSizes = {};
        }

        // Fonction pour mesurer et stocker les tailles des éléments
        function measureAndStoreSizes() {
            document.querySelectorAll('[id^="item-"]').forEach(el => {
                const id = el.id;
                if (id && id.startsWith("item-")) {
                    const parts = id.split('-');
                    if (parts.length >= 3) {
                        const itemId = parts[0] + '-' + parts[1];
                        const label = parts.slice(2).join(' ');

                        // Mesurer la taille de l'élément
                        const width = el.offsetWidth;
                        const height = el.offsetHeight;

                        // Chercher le label pattern_type dans le bloc
                        let patternType = null;
                        // On cherche un div qui contient 'Avec pattern' ou 'Sans pattern'
                        const typeDiv = Array.from(el.querySelectorAll('div'))
                            .find(div => div.textContent === 'Avec pattern' || div.textContent === 'Sans pattern');
                        if (typeDiv) {
                            patternType = typeDiv.textContent === 'Avec pattern' ? 'with' : 'without';
                        }

                        // Stocker les tailles
                        window.itemSizes[itemId] = {
                            width: width,
                            height: height,
                            label: label,
                            pattern_type: patternType
                        };
                    }
                }
            });
        }

        // Utiliser ResizeObserver pour observer les changements de taille
        if (!window.resizeObserverInitialized) {
            const observer = new ResizeObserver(entries => {
                // Mettre à jour les tailles lorsque les éléments sont redimensionnés
                measureAndStoreSizes();
                console.log("Updated item sizes:", window.itemSizes);
            });

            // Observer tous les éléments existants
            document.querySelectorAll('[id^="item-"]').forEach(el => {
                observer.observe(el);
            });

            // Observer les changements dans la timeline pour les nouveaux éléments
            const timeline = document.getElementById("timeline");
            if (timeline) {
                const mutationObserver = new MutationObserver(mutations => {
                    mutations.forEach(mutation => {
                        mutation.addedNodes.forEach(node => {
                            if (node.nodeType === 1 && node.id && node.id.startsWith("item-")) {
                                observer.observe(node);
                            }
                        });
                    });
                });
                mutationObserver.observe(timeline, { childList: true });
            }

            window.resizeObserverInitialized = true;
        }

        // Mesurer et stocker les tailles initiales
        measureAndStoreSizes();

        console.log("Current item sizes:", window.itemSizes);
        return window.itemSizes;
    }
    """,
    Output("size-store", "data"),
    Input("refresh-button", "n_clicks"),
    Input("timeline", "children")
)





if __name__ == '__main__':
    path = dlt.data_path

    if not os.path.exists(path):
        print('Creating directory ' + path + ' at root of the project')
        os.mkdir(path)

    if not os.path.exists(os.path.join(path, "export")):
        print('Creating directory ' + os.path.join(path, "export") + ' at root of the project')
        os.mkdir(os.path.join(path, "export"))

    if not os.path.exists(os.path.join(path, "exports")):
        print('Creating directory ' + os.path.join(path, "exports") + ' at root of the project')
        os.mkdir(os.path.join(path, "exports"))

    if not os.path.exists(os.path.join(path, "generated_data.csv")) \
            or not os.path.exists(os.path.join(path, "revenue.csv")):
        print('\nDownloading market data...\n')
        download_market_data()

    app.run(debug=True)