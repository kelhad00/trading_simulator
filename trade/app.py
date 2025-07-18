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
        try {
            window.itemSizes = {};

            function updateBlocks() {
                // Log de la largeur max de la timeline
                const timelineDiv = document.getElementById('timeline');
                if (timelineDiv) {
                    console.log('Largeur max de la timeline (offsetWidth):', timelineDiv.offsetWidth);
                } else {
                    console.log('Timeline non trouvée');
                }

                // Première passe : calculer la somme des largeurs des blocs valides
                let totalWidth = 0;
                const validElements = [];
                document.querySelectorAll('[id^="item-"]').forEach(el => {
                    let patternType = null;
                    const typeDiv = Array.from(el.querySelectorAll('div'))
                        .find(div => div.textContent === 'Avec pattern' || div.textContent === 'Sans pattern');
                    if (typeDiv) {
                        patternType = typeDiv.textContent === 'Avec pattern' ? 'with' : 'without';
                    }
                    if (patternType !== null) {
                        totalWidth += el.offsetWidth;
                        validElements.push(el);
                    }
                });

                validElements.forEach(el => {
                    const width = el.offsetWidth;
                    const height = el.offsetHeight;
                    const percent = (width / totalWidth) * 100;

                    // 1. Chercher le premier nœud texte non vide
                    let labelNode = null;
                    for (let node of el.childNodes) {
                        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim() !== "") {
                            labelNode = node;
                            break;
                        }
                    }
                    // 2. Sinon, chercher le premier enfant qui n'est pas un div (donc potentiellement span, strong, b, etc.)
                    if (!labelNode) {
                        for (let node of el.childNodes) {
                            if (
                                node.nodeType === Node.ELEMENT_NODE &&
                                node.tagName !== 'DIV'
                            ) {
                                labelNode = node;
                                break;
                            }
                        }
                    }

                    // 3. Modifier le texte si trouvé
                    if (labelNode) {
                        let displayedLabel = labelNode.textContent;
                        const percentRegex = /\s*\(\d+(\.\d+)?%\)$/;
                        displayedLabel = displayedLabel.replace(percentRegex, '').trim();
                        const newLabel = `${displayedLabel} (${percent.toFixed(1)}%)`;
                        labelNode.textContent = newLabel;
                    }
                    // 4. Adapter la largeur du bloc selon le pourcentage et la largeur de la timeline
                    if (timelineDiv) {
                        el.style.width = (timelineDiv.offsetWidth * percent / 100) + 'px';
                    }
                    // 5. Stocker les infos dans window.itemSizes (structure : width, height, label, pattern_type)
                    // label = nom brut extrait de l'id
                    let label = null;
                    const id = el.id;
                    if (id && id.startsWith("item-")) {
                        const parts = id.split('-');
                        if (parts.length >= 3) {
                            label = parts.slice(2).join(' ');
                        }
                    }
                    // pattern_type = with/without/null
                    let patternType = null;
                    const typeDiv = Array.from(el.querySelectorAll('div'))
                        .find(div => div.textContent === 'Avec pattern' || div.textContent === 'Sans pattern');
                    if (typeDiv) {
                        patternType = typeDiv.textContent === 'Avec pattern' ? 'with' : 'without';
                    }
                    window.itemSizes[el.id] = {
                        width: width,
                        height: height,
                        label: label,
                        pattern_type: patternType
                    };
                });
            }

            // Initial call
            updateBlocks();

            // Mettre en place un ResizeObserver sur chaque bloc valide
            const observers = [];
            document.querySelectorAll('[id^="item-"]').forEach(el => {
                // On évite de mettre plusieurs observers sur le même élément
                if (!el._resizeObserver) {
                    const observer = new ResizeObserver(() => {
                        updateBlocks();
                    });
                    observer.observe(el);
                    el._resizeObserver = observer;
                    observers.push(observer);
                }
            });

            return window.itemSizes;
        } catch (e) {
            console.error('Erreur dans le clientside_callback:', e);
            return {};
        }
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

    app.run(port=8050, debug=True)