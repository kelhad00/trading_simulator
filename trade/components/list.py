import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from trade.locales import translations as tls


def stock_list_element(stock, company, lang="fr", activity="", description=""):
    tl = tls[lang]["settings"]["tickers"]
    return dmc.Paper([
        html.Div([
            # Ticker column (read-only)
            html.Div([
                dmc.Text(tl["input"]["ticker"], weight=500),
                dmc.Text(stock, size="sm"),
            ], className="flex flex-col w-24 shrink-0"),

            # Company name column
            html.Div([
                dmc.Text(tl["input"]["company"], weight=500),
                dmc.Text(
                    company,
                    id={"type": "company-name-text", "index": stock},
                    size="sm",
                    style={"display": "block"},
                ),
                dmc.TextInput(
                    id={"type": "edit-stock-input", "index": stock},
                    value=company,
                    size="sm",
                    style={"display": "none"},
                ),
            ], className="flex flex-col flex-1"),

            # Activity column
            html.Div([
                dmc.Text(tl["input"]["activity"], weight=500),
                dmc.Text(
                    activity,
                    id={"type": "company-activity-text", "index": stock},
                    size="sm",
                    style={"display": "block"},
                ),
                dmc.TextInput(
                    id={"type": "edit-activity-input", "index": stock},
                    value=activity,
                    size="sm",
                    style={"display": "none"},
                ),
            ], className="flex flex-col flex-1"),

            # Description column
            html.Div([
                dmc.Text(tl["input"]["description"], weight=500),
                dmc.Text(
                    description or "—",
                    id={"type": "company-description-text", "index": stock},
                    size="sm",
                    style={"display": "block"},
                ),
                dmc.TextInput(
                    id={"type": "edit-description-input", "index": stock},
                    value=description or "",
                    size="sm",
                    style={"display": "none"},
                ),
            ], className="flex flex-col flex-[2]"),

        ], className="flex gap-4 items-start flex-1"),

        # Edit / Save / Delete buttons
        html.Div([
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
            dmc.ActionIcon(
                DashIconify(icon="material-symbols:delete-outline", width=20),
                size="lg",
                radius="md",
                color="dark",
                variant="outline",
                id={"type": "delete-stock", "index": stock},
                n_clicks=0,
            ),
        ], className="flex gap-1 shrink-0"),

    ],
        className="flex justify-between gap-4 items-center",
        radius="md",
        p="xs",
        withBorder=True,
    )
