"""Leaderboard: the participant against 20 robot traders, ranked by total assets.

The robots are made from the app's own market data: at the session's first candle
each robot spends most of the starting money on a random mix of the companies and
keeps the rest as cash. After that it never trades, so its value at every candle is
its cash + its shares x the Close price. A fixed seed gives every participant the
same robots.
"""
import numpy as np
import pandas as pd

from trade.utils.fees import rate, reserved

ROBOTS = 20
SEED = 2024
YOU = "You"

# One entry: (market dataframe, start, money, companies) -> robots' values
_cache: dict = {}


def total_assets(cashflow, totals, requests):
    """The participant's total: cash + money reserved for waiting buy orders + shares' value.

    Reserved money (fee included) is still the participant's: nothing has been
    bought with it yet, and a fee is only paid when an order is executed.
    """
    put_aside = sum(reserved(r) for r in (requests or []))
    shares_value = sum(v for v in (totals or {}).values() if v is not None and not pd.isna(v))
    return (cashflow or 0) + put_aside + shares_value


def _robot_holdings(prices, start_pos, initial_money, n=ROBOTS, seed=SEED, fee_pct=0):
    """What each robot bought at the session's first candle.

    Returns (tradable companies, {robot name: (cash, shares per tradable company)}).
    """
    start = prices.iloc[start_pos]
    tradable = [c for c in prices.columns if pd.notna(start[c]) and start[c] > 0]
    rng = np.random.default_rng(seed)

    holdings = {}
    for i in range(1, n + 1):
        cash_part = rng.uniform(0.05, 0.4)
        # Small alpha: most robots bet mostly on one or two companies, so they differ
        weights = rng.dirichlet(np.full(len(tradable), 0.5)) if tradable else np.array([])
        invested = initial_money * (1 - cash_part) if tradable else 0
        # `invested` pays for the shares and their fee
        shares = invested * weights / (start[tradable].to_numpy() * (1 + rate(fee_pct))) if tradable else weights
        holdings[f"Trader {i}"] = (initial_money - invested, shares)
    return tradable, holdings


def robot_assets(prices, start_pos, initial_money, n=ROBOTS, seed=SEED, fee_pct=0):
    """Each robot's total assets, one row per candle from `start_pos` on.

    `prices`: Close prices, one column per company. A company without a price at
    the start is not bought; a company whose data stops keeps its last price.
    `fee_pct`: the commission fee, paid by the robots on their one purchase, like
    the participant.
    """
    prices = prices.ffill()
    tradable, holdings = _robot_holdings(prices, start_pos, initial_money, n, seed, fee_pct)
    future = prices.iloc[start_pos:][tradable].to_numpy()
    values = {name: cash + (future @ shares if tradable else 0) for name, (cash, shares) in holdings.items()}
    return pd.DataFrame(values, index=prices.index[start_pos:])


def robots_at(market_df, timestamp, start_timestamp, initial_money, companies=None, fee_pct=0, price_now=None):
    """{robot name: total assets} at `timestamp`, or {} when it can't be worked out.

    `price_now(company)`: moving candles, while the candle at `timestamp` is still
    forming: the robots are valued at the price reached so far, like the
    participant, not at the Close the candle will reach (audit #6, 30 Oct 2026).
    A missing price falls back to the Close.
    """
    try:
        prices = market_df.xs('Close', axis=1, level=1)
        if companies:
            active = [c for c, info in companies.items() if info.get('got_charts') and c in prices.columns]
            prices = prices[active] if active else prices
        index = market_df.index
        start_pos = index.get_loc(start_timestamp)
        row = index.get_loc(timestamp) - start_pos
    except (KeyError, TypeError, AttributeError):
        return {}
    if row < 0:
        return {}

    key = (id(market_df), start_pos, initial_money, tuple(prices.columns), rate(fee_pct))
    if _cache.get('key') != key:
        _cache.update(key=key, market_df=market_df,    # kept so id() stays this dataframe's
                      robots=robot_assets(prices, start_pos, initial_money, fee_pct=fee_pct))
    robots = _cache['robots']
    if price_now is None:
        return robots.iloc[min(row, len(robots) - 1)].to_dict()

    if _cache.get('holdings_key') != key:
        _cache.update(holdings_key=key,
                      holdings=_robot_holdings(prices.ffill(), start_pos, initial_money, fee_pct=fee_pct))
    tradable, holdings = _cache['holdings']
    closes = prices.ffill().iloc[start_pos + min(row, len(robots) - 1)]
    now = []
    for c in tradable:
        p = price_now(c)
        now.append(float(p) if p is not None and pd.notna(p) else float(closes[c]))
    now = np.array(now)
    return {name: cash + (now @ shares if tradable else 0) for name, (cash, shares) in holdings.items()}


def ranking(robots, my_total):
    """Everyone sorted from richest to poorest, and the participant's rank.

    Equal totals share a rank (like at the very start, when everyone has the
    starting money); the participant is listed first among equals.
    Returns ([(rank, name, assets), ...], my_rank).
    """
    everyone = [(YOU, round(my_total, 2))] + [(name, round(v, 2)) for name, v in robots.items()]
    everyone.sort(key=lambda p: -p[1])       # stable: "You" stays first among equals
    table = [(1 + sum(1 for _, other in everyone if other > assets), name, assets)
             for name, assets in everyone]
    my_rank = next(rank for rank, name, _ in table if name == YOU)
    return table, my_rank
