from dash import Output, Input, State, callback, html
import dash_mantine_components as dmc

from trade.defaults import defaults as dlt
from trade.locales import translations as tls, language
from trade.utils.leaderboard import YOU, ranking, robots_at, total_assets
from trade.utils.market import get_market_dataframe, get_start_timestamp
from trade.utils.logs import get_logger

logger = get_logger("leaderboard")

TOP = 5     # rows shown; the participant's own rank is always on the last line
# At most 40% of the left column, scrolling inside if needed: the portfolio
# above always keeps the rest of the space (it can't be squashed to nothing)
_SHOWN = {"display": "flex", "maxHeight": "40%", "flexShrink": 0, "overflowY": "auto"}
_HIDDEN = {"display": "none"}


def _money(value):
    return f"{value:,.2f}€".replace(",", " ")


@callback(
    Output('leaderboard-box', 'style'),
    Output('leaderboard-container', 'children'),
    # timestamp changes only when a new candle appears: the board moves with the chart.
    # The participant's money changes it too, so a trade moves their rank straight away.
    Input('timestamp', 'data'),
    Input('portfolio-totals', 'data'),
    Input('cashflow', 'data'),
    Input('requests', 'data'),
    Input('leaderboard-enabled', 'data'),
    State('initial-bars', 'data'),
    State('initial-cashflow', 'data'),
    State('companies', 'data'),
    State("url", "search"),     # ?lang=en in this participant's address
    State('commission-fee', 'data'),
)
def update_leaderboard(timestamp, totals, cashflow, requests, enabled, initial_bars, initial_cashflow, companies, lang=None,
                       fee_pct=0):
    if not enabled:
        return _HIDDEN, None

    t = tls[language(lang)]['leaderboard']
    market_df = get_market_dataframe()
    if market_df is None:
        return _SHOWN, dmc.Text(t['unavailable'], size="sm", color="dimmed")

    start = get_start_timestamp(market_df, initial_bars)
    robots = robots_at(market_df, timestamp, start, initial_cashflow or dlt.initial_money, companies, fee_pct)
    if not robots:
        logger.debug("No robot values at %s (session start %s)", timestamp, start)
        return _SHOWN, dmc.Text(t['unavailable'], size="sm", color="dimmed")

    table, my_rank = ranking(robots, total_assets(cashflow, totals, requests))
    my_assets = next(assets for _, name, assets in table if name == YOU)

    def row(rank, name, assets):
        mine = name == YOU
        style = {"backgroundColor": "#e7f5ff", "fontWeight": "bold"} if mine else None
        return html.Tr([html.Td(rank), html.Td(t['you'] if mine else name), html.Td(_money(assets))], style=style)

    return _SHOWN, html.Div([
        dmc.Table(
            fontSize="xs",
            verticalSpacing=0,
            horizontalSpacing=4,
            children=[
                html.Thead(html.Tr([html.Th(t['rank']), html.Th(t['name']), html.Th(t['assets'])])),
                html.Tbody([row(*line) for line in table[:TOP]]),
            ],
        ),
        dmc.Text(t['my-rank'].format(rank=my_rank, total=len(table), assets=_money(my_assets)),
                 size="xs", weight=700, style={"paddingTop": "4px"}),
    ])
