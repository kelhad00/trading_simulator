from dash import html, dcc
import dash_mantine_components as dmc

from trade.locales import translations as tls
from trade.defaults import defaults as dlt
from trade.utils.graph.candlestick_charts import PLOTLY_CONFIG

from trade.components.menu import dashboard_menu as menu


def graph(lang="fr"):
    return dmc.Paper(
        className="col-span-5 row-span-3 col-start-3 flex flex-col gap-2",
        children=[
            html.Div([
                dmc.Select(
                    id='company-selector',
                    clearable=False,
                    persistence=True,
                    persistence_type='local',
                    className="w-full"
                ),
                
                html.Div([
                    dmc.Text(tls[lang]['price'], weight=700,
                             className="text-[rgb(73,80,87)] text-ellipsis", size="sm"),
                    dmc.Text(id="company-select-cash", className="whitespace-nowrap", size="sm"),
                ], className="flex flex-col"),
                html.Div([
                    dmc.Text("Date", weight=700,
                             className="text-[rgb(73,80,87)] text-ellipsis", size="sm"),
                    dmc.Text(id="timer", className="whitespace-nowrap", size="sm"),
                ], className="flex flex-col"),
                html.Div([
                    dmc.Text(tls[lang]['interval'], weight=700,
                             className="text-[rgb(73,80,87)] text-ellipsis", size="sm"),
                    dmc.SegmentedControl(
                        id="interval-selector",
                        value=dlt.granularity,
                        data=[
                            {"value": "h", "label": tls[lang]['interval-hour']},
                            {"value": "D", "label": tls[lang]['interval-day']},
                            {"value": "W", "label": tls[lang]['interval-week']},
                            {"value": "ME", "label": tls[lang]['interval-month']},
                        ],
                        size="xs",
                        className="mt-1"
                    ),
                ], className="flex flex-col"),
                menu(lang),
            ], className="flex gap-4 justify-between items-center"),

            dmc.SegmentedControl(
                id="segmented",
                value=tls[lang]['tab-market'],
                data=[tls[lang]['tab-market'], tls[lang]['tab-revenue']],
            ),

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

