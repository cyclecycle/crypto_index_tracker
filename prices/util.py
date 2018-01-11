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
