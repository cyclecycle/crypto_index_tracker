from prices.snapshots import get_single_price, PairNotListedError


def filter_unlisted_pairs(bases, quotes, exchanges):
    """Returns list of pairs listed on all input exchanges"""

    if isinstance(bases, str):
        bases = [bases]
    if isinstance(quotes, str):
        quotes = [quotes]
    if isinstance(exchanges, str):
        exchanges = [exchanges]

    pairs = []
    for e in exchanges:
        for b in bases:
            for q in quotes:
                try:
                    get_single_price(b, q, e)
                    pairs.append(b + '-' + q)
                except PairNotListedError:
                    pass

    return pairs


def calc_market_price(order_book, amount, side='buy'):
    """ Calculates price of market order based on current depth """
    if side == 'buy':
        depth = order_book['asks']
    elif side == 'sell':
        depth = order_book['bids']
    fill, cost = 0, 0
    while fill < amount:
        for order in depth:
            delta = min(order[1], (amount - fill))
            cost += order[0] * delta
            fill += delta
    assert fill == amount, 'fill: {}, amount: {}'.format(fill, amount)
    price = cost / fill
    return price
