from dash import html
import dash_mantine_components as dmc

from trade.locales import translations as tls

def news(lang="fr"):
    return dmc.Paper(
        [
            dmc.Text(tls[lang]['news'], weight=700, className="text-[rgb(73,80,87)]", size="xl"),
            html.Div(id="news-table", className="w-full h-full overflow-y-scroll"),
        ],
        id='news-container',
        className="col-span-3 row-span-2 row-start-4 overflow-scroll flex flex-col gap-4",
    )

def news_description(lang="fr"):
    return dmc.Paper(
        html.Div(
            className="flex flex-col gap-4",
            children=[
                dmc.Text(tls[lang]['title-news-description'], weight=700, className="text-[rgb(73,80,87)]", size="xl"),

                html.Div(
                    className="flex flex-col gap-2 flex-1",
                    children=[
                        dmc.Text(id="description-title", weight=500, className="text-[rgb(73,80,87)] text-ellipsis leading-none", size="md"),
                        dmc.Text(id='description-text', size="xs"),
                    ]
                ),

                dmc.Button(tls[lang]['button-news-description'], id='back-to-news-list', n_clicks=0, variant="outline", color="gray", fullWidth=True),
            ]
        ),
        id='description-container',
        className="col-span-3 row-span-2 row-start-4 overflow-scroll",
        style={'display': 'none'},
    )


