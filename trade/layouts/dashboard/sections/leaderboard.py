from dash import html
import dash_mantine_components as dmc

from trade.locales import translations as tls


def leaderboard(lang="fr"):
    """Ranking box under the portfolio. Hidden until the Settings switch turns it on
    (callbacks/dashboard/leaderboard.py), so the portfolio keeps its full height."""
    return dmc.Paper(
        id="leaderboard-box",
        className="flex flex-col gap-1",
        p="xs",
        style={"display": "none"},
        children=[
            dmc.Text(tls[lang]['leaderboard']['title'], weight=700, size="md"),
            html.Div(id="leaderboard-container"),
        ],
    )
