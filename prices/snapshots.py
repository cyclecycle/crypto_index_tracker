from cryptocompy import coin, price
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
import datetime
import time
import pandas as pd

""" Price snapshot functions using cryptocompy """

EXCHANGE_WHITELIST = {'GDAX', 'Kraken', 'Bitstamp', 'BitTrex', 'Bitfinex', 'Exmo', 'Binance'}  # incomplete


def get_single_price(base, quote, exchange, ret_float=False):
    """
    Get price of a single pair. Will check both directions (e.g. BTC-LTC and LTC-BTC).
    :param base: base curr (or quote if reversed)
    :param quote: quote curr (or base if reversed)
    :param exchange: exchange str
    :param ret_float: optionally return price as float
    :return: returns price as dict
    """
    assert (isinstance(base, str) and isinstance(quote, str)), 'Single pair only'
    p = price.get_current_price(base, quote, e=exchange)
    if 'Type' in p:
        p = price.get_current_price(quote, base, e=exchange)
        assert 'Type' not in p, p['Message']
        p = {base: {quote: 1/p[quote][base]}}
    return p if not ret_float else p[base][quote]


def compare_single_pair_prices(base, quote, exchanges):
    """Returns DF of exchange prices for single pair."""
    assert (isinstance(base, str) and isinstance(quote, str)), 'Single pair only'
    code = base + '-' + quote
    df = pd.DataFrame(columns=[code, 'price'])
    prices = []
    codes = []
    for ex in exchanges:
        prices.append(get_single_price(base, quote, ex, ret_float=True))
        codes.append(ex)
    df[code] = codes
    df['price'] = prices
    return df.sort_values(by='price')


def compare_two_exchanges(base, quote, e1, e2):
    """Compares one or more pair prices for 2 exchanges."""
    if isinstance(base, str) and isinstance(quote, str):
        ex1 = get_single_price(base, quote, e1)
        ex2 = get_single_price(base, quote, e2)
    else:
        ex1 = price.get_current_price(base, quote, e=e1)
        assert 'Type' not in ex1, ex1['Message']
        ex2 = price.get_current_price(base, quote, e=e2)
        assert 'Type' not in ex2, ex2['Message']

    df = pd.DataFrame(columns=['Pair', e1, e2, '% diff'])
    for b in ex1:
        for q in ex1[b]:
            row = {
                'Pair': b + '-' + q,
                e1: ex1[b][q],
                e2: ex2[b][q],
                '% diff': 100 * (ex1[b][q]/ex2[b][q] - 1)
            }
            df = df.append(row, ignore_index=True)
    return df


def find_matching_pairs(e1, e2):
    """Returns list of currency pairs listed on both input exchanges. Also checks reverse pairs."""
    # this is actually pretty difficult with this library!



def exchange_search(base, quote):
    """Returns exchanges that have markets for a single price pair. Also checks reverse pairs."""
    coin_data = coin.get_coin_snapshot(base, quote)
    exchanges1 = set([e['MARKET'] for e in coin_data['Exchanges']])
    coin_data = coin.get_coin_snapshot(quote, base)
    exchanges2 = set([e['MARKET'] for e in coin_data['Exchanges']])
    return list(exchanges1 | exchanges2)


if __name__ == '__main__':
    print(compare_two_exchanges(['ETH', 'LTC'], 'BTC', 'Kraken', 'Binance'))