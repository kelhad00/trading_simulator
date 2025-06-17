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
        dcc.Store(id="nb_export", data=len(os.listdir(os.path.join(dlt.data_path, "exports")))-1, storage_type="session"),
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
        if (!window.itemSizesInitialized) {
            window.itemSizes = {};
            window.itemSizesInitialized = true;

            const observer = new ResizeObserver(entries => {
                entries.forEach(entry => {
                    const id = entry.target.id;
                    if (id && id.startsWith("item-")) {
                        const el = entry.target;
                        const directText = Array.from(el.childNodes)
                            .filter(node => node.nodeType === Node.TEXT_NODE)
                            .map(node => node.textContent.trim())
                            .filter(text => text.length > 0)
                            .join(" ");

                        window.itemSizes[id] = {
                            width: entry.contentRect.width,
                            height: entry.contentRect.height,
                            label: directText
                        };
                    }
                });
            });

            function observeTextChanges(el, id) {
                const textObserver = new MutationObserver(() => {
                    const directText = Array.from(el.childNodes)
                        .filter(node => node.nodeType === Node.TEXT_NODE)
                        .map(node => node.textContent.trim())
                        .filter(text => text.length > 0)
                        .join(" ");

                    if (window.itemSizes[id]) {
                        window.itemSizes[id].label = directText;
                    }
                });

                textObserver.observe(el, { characterData: true, childList: true, subtree: true });
                el._textObserver = textObserver;
            }

            function observeExisting() {
                document.querySelectorAll('[id^="item-"]').forEach(el => {
                    const id = el.id;
                    observer.observe(el);
                    observeTextChanges(el, id);
                });
            }

            observeExisting();

            const timeline = document.getElementById("timeline");
            if (timeline) {
                const mutationObserver = new MutationObserver(mutations => {
                    mutations.forEach(mutation => {
                        mutation.addedNodes.forEach(node => {
                            if (node.nodeType === 1 && node.id && node.id.startsWith("item-")) {
                                observer.observe(node);
                                observeTextChanges(node, node.id);
                            }
                        });
                        mutation.removedNodes.forEach(node => {
                            if (node.nodeType === 1 && node.id && node.id.startsWith("item-")) {
                                delete window.itemSizes[node.id];
                                if (node._textObserver) {
                                    node._textObserver.disconnect();
                                    delete node._textObserver;
                                }
                            }
                        });
                    });
                });
                mutationObserver.observe(timeline, { childList: true, subtree: false });
            }
        }

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