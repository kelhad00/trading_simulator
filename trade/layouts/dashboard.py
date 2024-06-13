from dash import html, dcc, dash_table
from dash_iconify import DashIconify

from trade.Locales import translations as tls
from trade.candlestick_charts import PLOTLY_CONFIG
from trade.defaults import defaults as dlt

import dash_mantine_components as dmc


def main_layout(lang="fr"):
    return dmc.NotificationsProvider(
        html.Div([
            store(),
            html.Div(id="notifications-container"),
            html.Div([
                portfolio(lang),
                graph(lang),
                news(lang),
                request(lang)
            ], className="grid grid-cols-7 grid-rows-5 gap-4 h-screen w-screen bg-gray-100 p-4")
        ]))


def menu(lang="fr"):
    en_bg = ""
    fr_bg = ""

    if lang == "fr" :
        fr_bg = "bg-gray-100"
    else:
        en_bg = "bg-gray-100"

    return dmc.Menu(
        [
            dmc.MenuTarget(
                dmc.ActionIcon(
                    DashIconify(icon="carbon:settings"),
                    size="lg",
                    variant="outline",
                )
            ),
            dmc.MenuDropdown(
                [
                    dmc.MenuLabel("Simulation"),
                    dmc.MenuItem("Pause", icon=DashIconify(icon="carbon:pause"), id="pause-button", href=f"/?lang={lang}"),
                    dmc.MenuItem("Reset", icon=DashIconify(icon="carbon:reset"), id="reset-button", n_clicks=0, color="red"),
                    dmc.MenuDivider(),
                    dmc.MenuLabel("Language"),
                    dmc.MenuItem("Français", icon=DashIconify(icon="twemoji:flag-france"), href="/dashboard?lang=fr", n_clicks=0, className=fr_bg),
                    dmc.MenuItem("English", icon=DashIconify(icon="twemoji:flag-united-states"), href="/dashboard?lang=en", n_clicks=0, className=en_bg),
                ],
            )
        ], position="left-start"
    )


def request(lang="fr"):
    return html.Div([
        request_form(lang),
        request_list(lang)
    ], className="col-span-4 row-span-2 col-start-4 row-start-4 flex gap-4 justify-between")


def store():
    return html.Div([
        dcc.Interval(
            id='periodic-updater',
            interval=5000,
        ),
        # html.Span(id="timer", className="hidden"),
    ])


def portfolio(lang="fr"):
    return html.Div([
        html.Div([
            portfolio_cashflow(lang),
            portfolio_investment(lang),
        ], className="flex gap-2 justify-between flex-wrap"),
        portfolio_table(lang),
    ], className="col-span-2 row-span-3 flex flex-col gap-2 h-full w-full")


def portfolio_cashflow(lang="fr"):
    return dmc.Paper([
            dmc.Text(tls[lang]['portfolio-cashflow'], weight=700,
                     className="text-[rgb(73,80,87)] text-ellipsis leading-none", size="sm"),
            dmc.Text(weight=500, size="xl", id="portfolio-cashflow"),
        ],
        p="sm", radius="md",  withBorder=True,
        className="flex-1 flex flex-col justify-between",
    )


def portfolio_investment(lang="fr"):
    return dmc.Paper([
            dmc.Text(tls[lang]['portfolio-investment'], weight=700,
                     className="text-[rgb(73,80,87)] text-ellipsis leading-none", size="sm"),
            dmc.Text(weight=500, size="xl", id="portfolio-investment"),
        ],
        p="sm", radius="md",  withBorder=True,
        className="flex-1 flex flex-col gap-2 justify-between",
    )


def portfolio_table(lang="fr"):
    return dmc.Paper([
            dmc.Text(tls[lang]['portfolio'], weight=700, className="text-[rgb(73,80,87)]", size="xl"),
            html.Div(id='portfolio-table-container', className="h-full w-full overflow-y-scroll"),
        ],
        p="sm",
        radius="md",
        
        withBorder=True,
        className="flex-1 overflow-hidden flex flex-col gap-2"
    )




def graph(lang="fr"):
    options = {**dlt.companies, **dlt.indexes}

    return dmc.Paper(
        className="col-span-5 row-span-3 col-start-3 flex flex-col gap-2",
        p="sm",
        radius="md",
        withBorder=True,
        children=[
            html.Div([
                dmc.Select(
                    id='company-selector',
                    value=list(dlt.companies.keys())[0],
                    data=[{"label": v, "value": k} for k, v in options.items()],
                    clearable=False,
                    persistence=True,
                    persistence_type='local',
                    className="w-full"
                ),
                html.Div([
                    dmc.Text("Date", weight=700,
                             className="text-[rgb(73,80,87)] text-ellipsis", size="sm"),
                    dmc.Text(id="timer", className="whitespace-nowrap", size="sm"),

                ], className="flex flex-col"),
                menu(lang),
            ], className="flex gap-4 justify-between items-center"),
            dmc.SegmentedControl(
                id="segmented",
                value=tls[lang]['tab-market'],
                data=[tls[lang]['tab-market'], tls[lang]['tab-revenue']],
            ),
            dmc.Text(id="segmented-value"),
            html.Div(className="flex-1 overflow-hidden", children=[
                dcc.Graph(
                    id='company-graph',
                    config=PLOTLY_CONFIG,
                    className="w-full h-full",
                ),
                dcc.Graph(
                    id='revenue-graph',
                    config=PLOTLY_CONFIG,
                    className="w-full h-full",
                )
            ]),
        ])


def news(lang="fr"):
    return dmc.Paper(
        [
            dmc.Text(tls[lang]['news'], weight=700, className="text-[rgb(73,80,87)]", size="xl"),
            html.Div(id="news-table", className="w-full h-full overflow-y-scroll"),
        ],
        id='news-container',
        className="col-span-3 row-span-2 row-start-4 overflow-scroll flex flex-col gap-4",
        p="sm",
        radius="md",
        
        withBorder=True,
    )


def news_description(lang="fr"):
    return html.Div([
        html.H2(tls[lang]['title-news-description']),
        html.Article([
            html.Button(tls[lang]['button-news-description'], id='back-to-news-list'),
            html.H3(id='description-title'),
            html.P(id='description-text')
        ], className="news-article"),
    ], id='description-container', className="news-container", style={'display': 'none'})


def request_form(lang="fr"):
    return dmc.Paper(
        [
            html.Div(className="flex flex-col gap-2", children=[
                dmc.Text(tls[lang]['request-title'], weight=700, className="text-[rgb(73,80,87)]", size="xl"),
                dmc.SegmentedControl(
                    id="action-input",
                    value=tls[lang]['request-action']['choices'][0]["value"],
                    data=tls[lang]['request-action']['choices'],
                    size="xs",
                    className="w-full"
                ),
                dmc.NumberInput(
                    id='price-input',
                    label=dmc.Text(tls[lang]['request-price'], weight=700, className="text-[rgb(73,80,87)]", size="sm"),
                    value=0,
                    min=0,
                    step=1,
                ),
                dmc.NumberInput(
                    id='nbr-share-input',
                    label=dmc.Text(tls[lang]['request-shares'], weight=700, className="text-[rgb(73,80,87)]",
                                   size="sm"),
                    value=1,
                    min=1,
                    step=1,
                ),
            ]),
            dmc.Button(tls[lang]['submit-request'], id='submit-button', n_clicks=0, variant="outline", color="gray"),
            dmc.Text(id='request-err', size="xs")
        ],
        className="flex flex-col justify-between flex-1",
        p="sm",
        radius="md",
        
        withBorder=True,
    )


def request_list(lang="fr"):
    return dmc.Paper([
        dmc.Text(tls[lang]['requests-list-title'], weight=700, className="text-[rgb(73,80,87)]", size="xl"),
        dmc.Button(tls[lang]['clear-all-requests-button'], id="clear-done-btn", variant="outline", color="gray"),
        html.Div(id="request-table", className="overflow-y-scroll"),
    ],
        className="flex flex-col gap-2 flex-[2] overflow-hidden",
        p="sm",
        radius="md",
        
        withBorder=True,
    )


def legacy_graph(lang="fr"):
    return html.Div([
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

        html.Button("reset", id="reset-button"),

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
    ], className="graph-container")
