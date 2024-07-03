from dash import html
import dash_mantine_components as dmc

from trade.locales import translations as tls

def request(lang="fr"):
    return html.Div([
        request_form(lang),
        request_list(lang)
    ], className="col-span-4 row-span-2 col-start-4 row-start-4 flex gap-4 justify-between")


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
                    value=0, min=0, step=1,
                ),
                dmc.NumberInput(
                    id='nbr-share-input',
                    label=dmc.Text(tls[lang]['request-shares'], weight=700, className="text-[rgb(73,80,87)]", size="sm"),
                    value=1, min=1, step=1,
                ),
            ]),
            dmc.Button(tls[lang]['submit-request'], id='submit-button', n_clicks=0, variant="outline", color="gray"),
            dmc.Text(id='request-err', size="xs")
        ],
        className="flex flex-col justify-between flex-1",
    )


def request_list(lang="fr"):
    return dmc.Paper([
        dmc.Text(tls[lang]['requests-list-title'], weight=700, className="text-[rgb(73,80,87)]", size="xl"),
        dmc.Button(tls[lang]['clear-all-requests-button'], id="clear-done-btn", variant="outline", color="gray"),
        html.Div(id="request-table", className="overflow-y-scroll"),
    ], className="flex flex-col gap-2 flex-[2] overflow-hidden")
