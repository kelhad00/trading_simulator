"""Discrete mode: the session is a list of trials (episodes) instead of a running clock.

The researcher lists candle numbers, e.g. "10, 15". Trial 1 shows candles 1 to 10
and waits; the participant reads the news and places orders as long as they like,
then clicks "Next trial". The app then checks the waiting orders on every candle
the participant doesn't watch (11, 12, 13, 14, 15) and shows candles 1 to 15.
After the last trial the session ends.

Candle numbers count from 1, like on the chart: candle n is row n-1 of the data.
"""
import pandas as pd

from trade.utils.orders import fill_orders


def parse_checkpoints(text, n_candles):
    """'10, 15, 150' -> [10, 15, 150], or None when the list isn't valid.

    Valid: whole numbers from 2 to the number of candles in the data, each one
    bigger than the one before. (Candle 1 alone isn't a chart.)
    """
    try:
        numbers = [int(part) for part in str(text).replace(';', ',').split(',') if part.strip()]
    except ValueError:
        return None
    if not numbers or numbers[0] < 2 or numbers[-1] > n_candles:
        return None
    if any(b <= a for a, b in zip(numbers, numbers[1:])):
        return None
    return numbers


def history_bars(checkpoints):
    """The 'history candles at start' that makes the session open on the first trial."""
    return checkpoints[0] - 1


def candle_number(index, timestamp):
    """Number (from 1) of the candle at `timestamp`, or None when it isn't in the data."""
    try:
        return index.get_loc(timestamp) + 1
    except (KeyError, TypeError):
        return None


def trial_position(checkpoints, number):
    """(trial number from 1, number of trials) for the candle shown now."""
    done = sum(1 for c in checkpoints if c <= number)
    return max(done, 1), len(checkpoints)


def next_checkpoint(checkpoints, number):
    """The next trial's candle number, or None when the last trial is shown."""
    return next((c for c in checkpoints if c > number), None)


def walk_orders(market_df, from_number, to_number, request_list, port_shares, cashflow, cost_basis, sold_data):
    """Check the waiting orders on candles from_number+1 .. to_number, one by one,
    with the same rules as the live session: a buy fills at the first candle whose
    Low reaches its price, at no more than that price (and no more than the
    candle's close); a sell the same way with the High.

    `port_shares` is a {company: shares} dict. Lists and dicts are updated in place.
    Returns (port_shares, cashflow).
    """
    shares = pd.DataFrame.from_dict(port_shares, orient='index', columns=['Shares'])
    for row in range(from_number, to_number):          # row n = candle n + 1
        candle = market_df.iloc[row]

        def price_range(company, candle=candle):
            low, high = candle.get((company, 'Low')), candle.get((company, 'High'))
            if pd.isna(low) or pd.isna(high):
                return float('inf'), float('-inf')     # no data that day: nothing fills
            return low, high

        def price_now(company, candle=candle):
            return candle.get((company, 'Close'))

        cashflow = fill_orders(request_list, shares, cashflow, cost_basis, sold_data, price_range, price_now)
        if not request_list:
            break
    return shares['Shares'].to_dict(), cashflow
