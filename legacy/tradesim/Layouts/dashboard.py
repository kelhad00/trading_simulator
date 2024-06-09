from dash import html, dcc, dash_table
import pandas as pd

from tradesim.Components.candlestick_charts import PLOTLY_CONFIG
from tradesim.defaults import defaults as dlt
from tradesim.Locales import translations as tls


def add_state_components():
    """ Provide dcc.Store components in global scope
		to keep their state between page changes
	"""
    return [
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='nbr-logs', data=0),  # Number of times the trade state has been saved
        # Store timestamp value in the browser
        dcc.Store(id='market-timestamp-value', data='', storage_type='local'),
        dcc.Store(id='market-dataframe'),
        dcc.Store(id='price-dataframe'),
        dcc.Store(id='news-dataframe'),
        dcc.Store(id='cashflow', data=dlt.initial_money, storage_type='local'),
        dcc.Store(id='request-list', data=[], storage_type='local'),
        dcc.Store(  # Store only the number of shares for each company
            id='portfolio_shares',
            data={c: {'Shares': 0} for c in dlt.companies.keys()},
            storage_type='local'
        ),
        dcc.Store(  # Store only the total price for each company
            id='portfolio_totals',
            data={c: {'Total': 0} for c in dlt.companies.keys()},
            storage_type='local'
        ),
    ]


# Layout of the trade
def main_layout(lang="fr"):
    return html.Div([
        # Periodic updater
        dcc.Interval(
            id='periodic-updater',
            interval=dlt.update_time,  # in milliseconds
        ),

        #### Upper part ####

        # Portfolio
        html.Div([
            html.H2(tls[lang]['portfolio']),
            html.Div(id='portfolio-table-container'),
            dcc.Markdown(id='portfolio-total-price')
        ], className="portfolio-container"),

        # Company graph
        html.Div([
            dcc.Dropdown({**dlt.companies, **dlt.indexes}, list(dlt.companies.keys())[0],
                         id='company-selector',
                         clearable=False,
                         persistence=True,
                         persistence_type='local',
                         ),
            # Pause button
            dcc.Link(html.I(className="pause-icon"), href='/' + lang, className="pause-btn"),
            # Dropdown to change the language
            html.Div([
                html.Button([
                    html.Span(lang), html.Span(className="arrow")
                ]),
                html.Ul([
                    html.Li(dcc.Link(l, href=f'/{l}/dashboard')) for l in tls.keys() if l != lang
                ])
            ], className="switch-lang-btn"),
            dcc.Tabs([
                dcc.Tab([
                    dcc.Graph(
                        id='company-graph',
                        config=PLOTLY_CONFIG,
                        style={'width': '100%', 'height': '40vh'},
                    )
                ], label=tls[lang]['tab-market'], value='tab-market'),
                dcc.Tab([
                    dcc.Graph(
                        id='revenue-graph',
                        config=PLOTLY_CONFIG,
                        style={'width': '100%', 'height': '40vh'},
                    ),
                ], label=tls[lang]['tab-revenue'], value='tab-revenue', id='tab-revenue'),
            ], id="graph-tabs", value='tab-market'),
        ], className="graph-container"),

        #### Lower part ####

        # News
        html.Div([
            html.H2(tls[lang]['news']),

            dash_table.DataTable(
                id='news-table',
                columns=[
                    {'name': tls[lang]['news-table']['date'], 'id': 'date'},
                    {'name': tls[lang]['news-table']['article'], 'id': 'article'}
                ],
                fixed_rows={'headers': True, 'data': 0},  # Allow to scroll the table
                page_size=1000000000,  # Display all the news on the same page
            )
        ], id='news-container', className="news-container"),

        # Add the component with the description
        html.Div([
            html.H2(tls[lang]['title-news-description']),

            html.Article([
                html.Button(tls[lang]['button-news-description'], id='back-to-news-list',
                            # style = {'border' : 'none', 'padding-top' : 5, 'padding-bottom' : 5, 'border-radius' : 10}
                            ),
                html.H3(id='description-title'),
                html.P(id='description-text')
            ], className="news-article"),

        ], id='description-container', className="news-container", style={'display': 'none'}),

        # Requests
        html.Div([
            html.H2(tls[lang]['request-title']),

            html.Label(tls[lang]['request-action']['label'], htmlFor='action-input'),
            dcc.RadioItems(
                options=tls[lang]['request-action']['choices'],
                value='buy',
                id="action-input",
                inline=True
            ),

            html.Label(tls[lang]['request-price'], htmlFor='price-input'),
            dcc.Input(id='price-input', value=0, type='number', min=0, step=0.1),

            html.Label(tls[lang]['request-shares'], htmlFor='nbr-share-input'),
            dcc.Input(id='nbr-share-input', value=1, type='number', min=1, step=1),

            html.Button(tls[lang]['submit-request'], id='submit-button', n_clicks=0),

            html.P(id='request-err')
        ], className="request-form-container"),

        html.Div([
            html.H2(tls[lang]['requests-list-title']),
            dash_table.DataTable(
                id='request-table',
                columns=[
                    {'name': tls[lang]['requests-table']['actions'], 'id': 'actions'},
                    {'name': tls[lang]['requests-table']['shares'], 'id': 'shares'},
                    {'name': tls[lang]['requests-table']['company'], 'id': 'company'},
                    {'name': tls[lang]['requests-table']['price'], 'id': 'price'}
                ],
                row_selectable='multi',
                selected_rows=[],
                cell_selectable=False
            ),
            html.Button(tls[lang]['clear-all-requests-button'], id="clear-done-btn"),
        ], className="request-list-container")

    ], className="dashboard-container")
