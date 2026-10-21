"""Executing waiting orders: the same rules for the live candle and for the
candles a discrete-mode trial jumps over (trade/utils/trials.py)."""
from trade.utils.fees import buy_cost, sell_proceeds, reserved


def fill_orders(request_list, port_shares, cashflow, cost_basis, sold_data, price_range, price_now):
    """Execute the waiting orders the market reached; the others keep waiting.

    The same rules for every mode: the live candle (execute_requests) and the
    candles a discrete-mode trial jumps over (trade/utils/trials.py).
    Args:
        request_list: waiting orders; executed ones are removed from it
        port_shares: DataFrame of shares held (column 'Shares'), updated
        cost_basis, sold_data: dicts updated for Px Achat / Px Vente
        price_range(company): (low, high) the market reached
        price_now(company): price an executed order is filled at (at most a buy's
            limit, at least a sell's limit)
    Returns:
        the new cashflow
    """
    i = 0
    while i < len(request_list):
        req = request_list[i]
        low_price, high_price = price_range(req['company'])

        # If the request is completed
        if req['action'] == 'buy' and low_price <= req['price']:
            # A limit buy never pays more than the limit — if the market is actually
            # trading below it, fill at the (lower) market price and refund the
            # difference between what was reserved (at the limit price) and what was
            # really spent.
            fill_price = min(req['price'], price_now(req['company']))
            fee = req.get('fee', 0)
            port_shares.loc[req['company']] += req['shares']
            # The fee is part of what the shares cost (Px Achat and PnL include it)
            cost = buy_cost(req['shares'], fill_price, fee)
            cost_basis[req['company']] = cost_basis.get(req['company'], 0) + cost
            cashflow += reserved(req) - cost
            request_list.remove(req)

        # Same as above for the sell request
        elif req['action'] == 'sell' and high_price >= req['price']:
            # If the user has enough shares
            if port_shares.at[req['company'], 'Shares'] >= req["shares"]:
                # A limit sell never settles for less than the limit — if the market is
                # actually trading above it, fill at the (higher) market price.
                fill_price = max(req['price'], price_now(req['company']))
                # Update only the shares and the cashflow
                # Because the total price will be updated in the portfolio callback
                held_before = port_shares.at[req['company'], 'Shares']
                port_shares.loc[req['company']] -= req["shares"]
                # The fee is taken from the money received
                cashflow += sell_proceeds(req['shares'], fill_price, req.get('fee', 0))
                if held_before > 0:
                    avg = cost_basis.get(req['company'], 0) / held_before
                    cost_basis[req['company']] = cost_basis.get(req['company'], 0) - req['shares'] * avg
                sold_data.setdefault(req['company'], {"revenue": 0, "shares": 0})
                sold_data[req['company']]["revenue"] += req['shares'] * fill_price
                sold_data[req['company']]["shares"] += req['shares']

            # the request is removed, with or without the user having enough shares
            request_list.remove(req)

        # If the request is not completed yet, pass to the next one.
        # If the request is completed, the request is removed from the list and
        # the next request is now at the current index.
        else:
            i += 1

    return cashflow
