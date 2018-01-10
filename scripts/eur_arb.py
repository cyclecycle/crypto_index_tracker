from private import CLIENTS, ADDRESSES
from prices.snapshots import compare_two_exchanges_ccxt, compare_two_exchanges
import ccxt
import time

# NO BTC FOR NOW

COINS = {
    'GDAX': ['LTC', 'ETH'],
    'Bitstamp': ['LTC', 'ETH', 'XRP']
}


def get_best_arb(ex_buy, ex_sell):

    df = compare_two_exchanges(COINS[ex_sell], 'EUR', ex_sell, ex_buy)
    print(df)
    row = df['% diff'].idxmax()
    maxdiff = df['% diff'].max()
    pair = df['Pair'][row]
    print('Gain of {}% for {} buying on {} and selling on {}'.format(maxdiff, pair, ex_buy, ex_sell))


if __name__ == '__main__':
    get_best_arb('Kraken', 'GDAX')
