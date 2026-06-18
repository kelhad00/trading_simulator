from dash import html, dcc
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import os

from trade.locales import translations as tls
from trade.defaults import defaults as dlt

from trade.components.header import header

APP_MODE = os.getenv('APP_MODE', 'config')

_UPLOAD_STYLE = {
    "width": "100%",
    "padding": "10px 16px",
    "borderWidth": "1px",
    "borderStyle": "dashed",
    "borderRadius": "6px",
    "borderColor": "#495057",
    "cursor": "pointer",
    "backgroundColor": "white",
    "fontSize": "14px",
    "color": "#495057",
}

_LOADED_STYLE = {
    "width": "100%",
    "padding": "10px 16px",
    "borderWidth": "1px",
    "borderStyle": "solid",
    "borderRadius": "6px",
    "borderColor": "#2f9e44",
    "backgroundColor": "#ebfbee",
    "fontSize": "14px",
    "color": "#2f9e44",
    "display": "none",
    "alignItems": "center",
    "justifyContent": "space-between",
    "gap": "8px",
}


def main_layout(lang="fr"):
    return html.Div([
        html.Div([
            header(lang, mode=APP_MODE),
            html.Div([
                welcome(lang),
                description(lang)
            ], className="flex flex-col gap-8"),
        ], className="flex flex-col gap-8"),
        options(lang)
    ], className="pt-8 pb-20 px-12 bg-gray-100 h-screen w-screen flex flex-col gap-8 justify-between")


def options(lang="fr"):
    tl = tls[lang]
    tl_session = tl["session"]

    def nav_button(label, href, icon, disabled=False, id=""):
        return html.A(
            dmc.Button(
                label,
                id=id,
                leftIcon=DashIconify(icon=icon),
                variant="solid", color="dark", radius="md", size="lg",
                disabled=disabled, fullWidth=True
            ),
            href=href,
            id=f"{id}-link" if id else None,
            style={
                "textDecoration": "none",
                "display": "block",
                "pointerEvents": "none" if disabled else "auto",
            }
        )

    if APP_MODE == 'runtime':
        return html.Div([
            dmc.Tooltip(
                id="start-tooltip",
                label=tl_session["start-tooltip"],
                withArrow=True,
                position="right",
                disabled=False,
                children=html.Span(
                    nav_button(tl["button-start"], "/dashboard?lang=" + lang,
                               "carbon:play-filled-alt", True, id="start-simulation-btn"),
                    style={"display": "block"},
                ),
            ),

            # Upload area — visible before import
            html.Div(
                id="session-upload-area",
                children=dcc.Upload(
                    id="upload-session",
                    children=html.Div([
                        DashIconify(icon="carbon:upload", width=20),
                        html.Span(tl_session["import-hint"], style={"marginLeft": "8px"}),
                    ], style={"display": "flex", "alignItems": "center"}),
                    accept=".zip",
                    style=_UPLOAD_STYLE,
                ),
            ),

            # Loaded indicator — hidden until import succeeds
            html.Div(
                id="session-loaded-area",
                style=_LOADED_STYLE,
                children=[
                    html.Div([
                        DashIconify(icon="carbon:checkmark-filled", width=18, color="#2f9e44"),
                        html.Span(tl_session["session-loaded-prefix"], style={"marginLeft": "6px", "fontWeight": "600"}),
                        html.Span(id="imported-filename", style={"marginLeft": "4px"}),
                    ], style={"display": "flex", "alignItems": "center"}),
                    dmc.ActionIcon(
                        DashIconify(icon="carbon:close", width=16),
                        id="clear-session-btn",
                        variant="transparent",
                        color="red",
                        size="sm",
                        title=tl_session["session-remove"],
                    ),
                ],
            ),

            dmc.Button(tl["button-restart-sim"], leftIcon=DashIconify(icon="carbon:reset"),
                       id="reset-button", color="dark", size="lg"),

            # Hidden div used as dummy output for the file-input reset clientside callback
            html.Div(id="_upload-reset", style={"display": "none"}),
        ], className="flex gap-4 flex-col max-w-xs")

    # Config mode — Settings + Reset only, no Start button
    return html.Div([
        nav_button(tl["button-settings"], "/settings?lang=" + lang, "carbon:settings", id="settings-button"),
        dmc.Button(tl["button-restart-sim"], leftIcon=DashIconify(icon="carbon:reset"),
                   id="reset-button", color="dark", size="lg"),
    ], className="flex gap-4 flex-col max-w-xs")


def description(lang="fr"):
    def variant(content):
        return html.Span(content, className="text-3xl font-semibold text-[rgb(73,80,87)]")

    return dmc.Text([
        tls[lang]["description"][0],
        variant(tls[lang]["description"][1]),
        tls[lang]["description"][2],
        variant(tls[lang]["description"][3]),
        tls[lang]["description"][4],
        variant(tls[lang]["description"][5]),
        tls[lang]["description"][6],
    ], className="text-3xl font-semibold max-w-2xl")


def welcome(lang="fr"):
    className = "text-8xl font-bold leading-none"
    return html.Div([
        dmc.Title(tls[lang]["welcome"][0], order=1, className=f"{className} text-[rgb(73,80,87)]"),
        dmc.Title(tls[lang]["welcome"][1], order=1, className=className),
    ])


def _files_missing():
    return not (
        os.path.exists(os.path.join(dlt.data_path, 'generated_data.csv'))
        and os.path.exists(os.path.join(dlt.data_path, 'news.csv'))
    )
