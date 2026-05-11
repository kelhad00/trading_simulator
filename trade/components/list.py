import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from trade.locales import translations as tls


def stock_list_element(stock, company, lang="fr"):
    tl = tls[lang]["settings"]["tickers"]
    return dmc.Paper([
        # Ticker column
        html.Div([
            dmc.Text(tl["input"]["ticker"], weight=500),
            dmc.Text(stock, size="sm"),
        ], className="flex flex-col flex-1"),

        # Company name column — holds both the read-only label and the edit input
        html.Div([
            dmc.Text(tl["input"]["company"], weight=500),
            # Read-only label (visible by default)
            dmc.Text(
                company,
                id={"type": "company-name-text", "index": stock},
                size="sm",
                style={"display": "block"},
            ),
            # Edit input (hidden by default)
            dmc.TextInput(
                id={"type": "edit-stock-input", "index": stock},
                value=company,
                size="sm",
                style={"display": "none"},
            ),
        ], className="flex flex-col flex-[2]"),

        # Edit / Save button group
        html.Div([
            # Edit button — visible in read-only mode
            dmc.ActionIcon(
                DashIconify(icon="material-symbols:edit-outline", width=20),
                id={"type": "edit-stock", "index": stock},
                n_clicks=0,
                size="lg",
                radius="md",
                color="dark",
                variant="subtle",
                style={"display": "flex"},
            ),
            # Save button — visible in edit mode
            dmc.ActionIcon(
                DashIconify(icon="material-symbols:check", width=20),
                id={"type": "save-stock", "index": stock},
                n_clicks=0,
                size="lg",
                radius="md",
                color="green",
                variant="subtle",
                style={"display": "none"},
            ),
        ], className="flex gap-1"),

        # Delete button — unchanged
        dmc.ActionIcon(
            DashIconify(icon="material-symbols:delete-outline", width=20),
            size="lg",
            radius="md",
            color="dark",
            variant="outline",
            id={"type": "delete-stock", "index": stock},
            n_clicks=0,
        ),
    ],
        className="flex justify-between gap-4 items-center",
        radius="md",
        p="xs",
        withBorder=True,
    )
