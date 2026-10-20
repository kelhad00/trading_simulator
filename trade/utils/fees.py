"""Commission fees: a percentage paid on every executed buy and sell.

Example with a 0.05% fee: buying 100€ of shares costs 100.05€, selling 100€ of
shares brings in 99.95€.

Each order remembers the fee that applied when it was placed (key 'fee'), so the
money put aside for it stays right even if the researcher changes the fee during
a session. Orders without the key (placed before fees existed) have no fee.
"""


def rate(fee_pct):
    """The fee as a fraction: 0.05 (%) -> 0.0005. Missing or invalid -> 0."""
    try:
        return max(float(fee_pct or 0), 0) / 100
    except (TypeError, ValueError):
        return 0


def buy_cost(shares, price, fee_pct):
    """What buying costs: the shares' price plus the fee."""
    return shares * price * (1 + rate(fee_pct))


def sell_proceeds(shares, price, fee_pct):
    """What selling brings in: the shares' price minus the fee."""
    return shares * price * (1 - rate(fee_pct))


def max_buy_shares(money, price, fee_pct):
    """Most whole shares that `money` can buy, fee included."""
    unit = buy_cost(1, price, fee_pct)
    return int(money // unit) if unit > 0 else 0


def reserved(req):
    """Money put aside for a waiting order: a buy's price and fee, nothing for a sell."""
    if req.get('action') != 'buy':
        return 0
    return buy_cost(req.get('shares', 0), req.get('price', 0), req.get('fee', 0))
