from cryptocompy import coin, price
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import pandas as pd
from trade.util import calc_market_price
from ccxt.base.errors import ExchangeError

""" Price snapshot functions using cryptocompy """

EXCHANGE_WHITELIST = {'GDAX', 'Kraken', 'Bitstamp', 'BitTrex', 'Bitfinex', 'Exmo', 'Binance'}  # incomplete
pd.set_option('expand_frame_repr', False)

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
        if 'Type' in p:
            raise PairNotListedError('{}-{} pair (or reverse) not listed on {}'.format(base, quote, exchange))
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
    """
    Compares one or more pair prices for 2 exchanges.
    """
    if isinstance(base, str) and isinstance(quote, str):
        ex1 = get_single_price(base, quote, e1)
        ex2 = get_single_price(base, quote, e2)
    else:
        ex1 = price.get_current_price(base, quote, e=e1)
        ex2 = price.get_current_price(base, quote, e=e2)
        if 'Type' in ex1 or 'Type' in ex2:
            raise PairNotListedError('One or more pairs not listed in both exchanges')

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


def compare_order_books(base, quote, clients):
    """
    Compares bids and asks to find maximum % difference between prices on ccxt clients for pairs.
    """
    if isinstance(base, str):
        base = [base]
    if isinstance(quote, str):
        quote = [quote]

    cols = ['pair']
    for client in clients:
        cols += [client.describe()['name'] + ' ask', client.describe()['name'] + ' bid']
    cols += ['% diff', 'buy', 'sell']
    df = pd.DataFrame(columns=cols)

    for b in base:
        for q in quote:
            pair = b + '/' + q
            row = {}
            for client in clients:
                try:
                    tick = client.fetch_ticker(pair)
                except ExchangeError:
                    tick = {'ask': None, 'bid': None}

                row[client.describe()['name'] + ' ask'] = tick['ask']
                row[client.describe()['name'] + ' bid'] = tick['bid']

            max_perc_diff = -100
            buy, sell = None, None
            for buy_client in row:
                if buy_client.endswith('ask'):
                    for sell_client in row:
                        if sell_client.endswith('bid'):
                            if row[sell_client] is not None and row[buy_client] is not None:
                                perc_diff = (row[sell_client] / row[buy_client] - 1) * 100
                                if perc_diff > max_perc_diff:
                                    buy = buy_client[:-4]
                                    sell = sell_client[:-4]
                                    max_perc_diff = perc_diff

            row['pair'] = pair
            row['buy'] = buy
            row['sell'] = sell
            row['% diff'] = max_perc_diff
            df = df.append(row, ignore_index=True)

    return df


def compare_actual_market_prices(base, quote, amount_in_eur, clients):
    """ Compares actual price for given base amount in EUR """

    amount_in_eur = amount_in_eur / price.get_current_price(base, 'EUR')[base]['EUR']

    cols = ['pair']
    for client in clients:
        cols += [client.describe()['name'] + ' buy', client.describe()['name'] + ' sell']
    df = pd.DataFrame(columns=cols)

    pair = base + '/' + quote
    row = {}

    row['pair'] = pair
    for client in clients:
        try:
            buy_price, sell_price = calc_market_price(base, quote, amount_in_eur, client)
        except ExchangeError:
            print('error')
            continue

        row[client.describe()['name'] + ' buy'] = buy_price
        row[client.describe()['name'] + ' sell'] = sell_price
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


class PairNotListedError(Exception):
    pass

if __name__ == '__main__':
    pass