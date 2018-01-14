import ccxt
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


def get_order_books(base, quote, client):
    """ Batch version of fetch order book ccxt function """
    if isinstance(base, str):
        base = [base]
    if isinstance(quote, str):
        quote = [quote]

    order_books = {}
    for b in base:
        for q in quote:
            pair = b + '/' + q
            order_books[pair] = client.fetch_order_book(pair)

    # NOTE: order book lengths are different for different clients
    return order_books


if __name__ == '__main__':
    ob = get_order_books('LTC', 'BTC', ccxt.kucoin())['LTC/BTC']
    print(ob)
    print(len(ob['asks']), len(ob['bids']))

