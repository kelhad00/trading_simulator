from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from trade.components.sections import section
from trade.locales import translations as tls


def news_settings(lang="fr"):
    tl = tls[lang]["settings"]["news"]
    tm = tl["manual"]
    return html.Div([
        dcc.Store(id="manual-positions-store", data={}, storage_type="session"),

        section(tl["subtitles"]["provider"], [
            dmc.RadioGroup(
                id="input-provider",
                label=tl["provider"]["label"],
                value="ollama",
                children=[
                    dmc.Radio(value="ollama", label=tl["provider"]["ollama"]),
                    dmc.Radio(value="groq",   label=tl["provider"]["groq"]),
                ],
                className="w-full",
            ),

            # Shown when provider == "ollama"
            html.Div([
                dmc.TextInput(
                    id="input-api-key",
                    label=tl["input"]["key"],
                    placeholder=tl["input"]["key-placeholder"],
                    className="flex-1",
                ),
            ], id="ollama-url-container", className="flex w-full"),

            # Shown when provider == "groq"
            html.Div([
                dmc.TextInput(
                    id="input-groq-key",
                    type="password",
                    label=tl["input"]["groq-key"],
                    placeholder=tl["input"]["groq-key-placeholder"],
                    className="flex-1",
                    rightSection=dmc.ActionIcon(
                        DashIconify(id="groq-eye-icon", icon="mdi:eye-off", width=18),
                        id="groq-eye-toggle",
                        variant="subtle",
                        color="gray",
                        size="sm",
                    ),
                ),
                dmc.Text(
                    tl["provider"]["groq-note"],
                    size="xs",
                    color="dimmed",
                    className="mt-1",
                ),
            ], id="groq-key-container", className="flex flex-col w-full", style={"display": "none"}),
        ]),

        section(tl["subtitles"]["parameters"], [
            html.Div([
                dmc.NumberInput(
                    id="input-alpha",
                    label=tl["input"]["alpha"],
                    className="flex-1",
                    value=0.5,
                ),
            ], className="flex w-full"),
            html.Div([
                dmc.NumberInput(
                    id="input-alpha-day-interval",
                    label=tl["input"]["alpha-day-interval"],
                    className="flex-1",
                    value=3,
                ),
            ], className="flex w-full"),
            html.Div([
                dmc.NumberInput(
                    id="input-delta",
                    label=tl["input"]["delta"],
                    className="flex-1",
                    value=0,
                ),
            ], className="flex w-full"),
        ]),

        section(tl["subtitles"]["mode"], [
            html.Div([
                dmc.RadioGroup(
                    id="input-generation-mode",
                    label=tl["radio"]["label"],
                    children=[
                        dmc.Radio(value="random", label=tl["radio"]["options"][0]),
                        dmc.Radio(value="linear", label=tl["radio"]["options"][1]),
                        dmc.Radio(value="manual", label=tl["radio"]["options"][2]),
                    ],
                    value="random",
                ),
            ], className="flex w-full"),

            # Random mode inputs
            html.Div([
                dmc.NumberInput(
                    id="input-nbr-positive-news",
                    label=tl["input"]["nbr-positive-news"],
                    className="flex-1",
                    value=2,
                ),
                dmc.NumberInput(
                    id="input-nbr-negative-news",
                    label=tl["input"]["nbr-negative-news"],
                    className="flex-1",
                    value=2,
                ),
            ], className="flex w-full", id="nbr-news-container"),

            # Linear mode inputs
            html.Div([
                dmc.NumberInput(
                    id="input-top-k",
                    label=tl["input"]["top-k"],
                    description=tl["input"]["top-k-description"],
                    className="flex-1",
                    value=0,
                    min=0,
                ),
            ], className="flex w-full", id="top-k-container", style={"display": "none"}),

            # Manual mode section
            html.Div([
                # Sentiment selector
                html.Div([
                    dmc.RadioGroup(
                        id="input-news-sentiment",
                        label=tm["sentiment-label"],
                        children=[
                            dmc.Radio(value="positive", label=tm["sentiment-positive"]),
                            dmc.Radio(value="negative", label=tm["sentiment-negative"]),
                        ],
                        value="positive",
                    ),
                ], className="flex w-full"),

                # Hover-to-aim indicator
                dmc.Text(
                    id="manual-hover-text",
                    size="sm",
                    color="dimmed",
                    children=tm["hover-text-idle"],
                ),

                # Position counter + clear button
                html.Div([
                    dmc.Text(id="manual-position-counter", size="sm", children=tm["counter-empty"]),
                    dmc.Button(
                        tm["clear"],
                        id="clear-manual-company",
                        color="red",
                        variant="outline",
                        size="xs",
                    ),
                ], className="flex items-center gap-4"),

                # Date picker backup
                html.Div([
                    dmc.DatePicker(
                        id="input-manual-date",
                        label=tm["date-label"],
                        className="flex-1",
                        clearable=True,
                    ),
                    dmc.Button(
                        tm["date-add"],
                        id="add-manual-date",
                        color="dark",
                        size="sm",
                        style={"alignSelf": "flex-end"},
                    ),
                ], className="flex items-center gap-4 w-full"),
            ], id="manual-section", style={"display": "none"}, className="flex flex-col gap-4 w-full"),

            # Notice shown in random/linear when manual positions are saved
            html.Div(id="manual-flagged-notice"),
        ]),

        section(tl["subtitles"]["preview"], [
            dmc.Select(
                id="news-select-company",
                label=tl["select"]["ticker"],
                className="w-full",
            ),
            dmc.Paper(
                dcc.Graph(id="news-chart")
            ),
        ]),

        dmc.Button(tl["button"]["generate"], id="generate-news", color="dark", size="md"),
        html.Div([], id="news-notification-container"),

    ], className="flex flex-col gap-8 w-full")
