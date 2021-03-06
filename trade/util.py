import os
from pathlib import Path
import pickle
import ccxt
# from forex_python.converter import CurrencyRates
import numpy as np
import pandas as pd
import time
import yaml
from cryptocompy import price

FIAT = ['GBP', 'USD', 'EUR']

CWD = os.path.dirname(os.path.realpath(__file__))
ROOT = Path(CWD).parents[0]
with open(os.path.join(ROOT, 'trade/api_keys.yaml')) as f:  # This file is in .gitignore so is individual
    API_KEYS = yaml.load(f)

# CLIENTS = {
#     'BINANCE': ccxt.binance(API_KEYS['BINANCE']),
#     # 'GDAX': ccxt.gdax(API_KEYS['GDAX'])
# }

def get_total_balance(clients, gbp_only=False, wallets=None, funds_invested=None):
    """
    Analyses balance of funds across one or more exchanges.

    Note: Prices for small coins like IOTA and XRB are currently incorrect on cryptocompare.

    :param clients: Dict of ccxt authenticated clients with exchange names as keys
    :param wallets: optional dict of coins held in private wallets (e.g. {'BTC': 1.1, 'LTC': 0.02})
    :param gbp_only: optionally return GBP values only
    :param funds_invested: optionally input GBP invested for profit calculation
    :return: DataFrame of balance
    """
    eur2gbp = CurrencyRates().get_rate('EUR', 'GBP')
    pd.set_option('expand_frame_repr', False)
    pd.options.display.float_format = '{:.2f}'.format

    # build df columns from currencies
    df_cols = ['Exchange']
    totals = {}
    coins = set()
    for ex in clients:
        totals_raw = clients[ex].fetch_balance()['total']
        totals[ex] = {}
        for curr in totals_raw:
            if totals_raw[curr] > 0.01:
                totals[ex][curr] = totals_raw[curr]
        for curr in totals[ex]:
            if curr not in FIAT:
                coins.add(curr)

    # add wallets
    totals['Wallets'] = {}
    for curr in wallets:
        totals['Wallets'][curr] = wallets[curr]
        coins.add(curr)

    df_cols += list(coins) + ['EUR', 'GBP', 'Total (GBP)']
    df = pd.DataFrame(columns=df_cols)
    avg_prices = price.get_current_price([c for c in coins if c != 'BTC'], 'BTC')
    btc2gbp = price.get_current_price('BTC', 'GBP')['BTC']['GBP']
    # print(avg_prices)
    # print(btc2gbp)

    # build row values for each exchange
    for ex in totals:
        row = {}
        total_gbp = 0
        for col in df:
            if col == 'Exchange':
                row['Exchange'] = ex
            elif col in totals[ex]:
                row[col] = totals[ex][col]
                if col == 'EUR':
                    total_gbp += row[col] * eur2gbp
                elif col == 'GBP':
                    total_gbp += row[col]
                elif col == 'BTC':
                    total_gbp += row[col] * btc2gbp
                else:
                    total_gbp += row[col] * avg_prices[col]['BTC'] * btc2gbp
            else:
                row[col] = 0.
        row['Total (GBP)'] = total_gbp
        df = df.append(row, ignore_index=True)

    # total all exchanges in each curr and GBP
    row_totals = {}
    row_gbp_totals = {}
    for col in df_cols:
        if col == 'Exchange':
            row_totals['Exchange'] = 'Total'
            row_gbp_totals['Exchange'] = 'Total (GBP)'
        else:
            row_totals[col] = sum(df[col].values)
            if col == 'EUR':
                row_gbp_totals[col] = row_totals[col] * eur2gbp
            elif col == 'GBP' or col == 'Total (GBP)':
                row_gbp_totals[col] = row_totals[col]
            elif col == 'BTC':
                row_gbp_totals[col] = row_totals[col] * btc2gbp
            else:
                row_gbp_totals[col] = row_totals[col] * avg_prices[col]['BTC'] * btc2gbp
    df = df.append(row_totals, ignore_index=True)
    df = df.append(row_gbp_totals, ignore_index=True)

    # add percentage of funds stored in each exchange
    perc_col = []
    for i, row in df.iterrows():
        if row['Exchange'] != 'Total':
            perc_col.append(100 * row['Total (GBP)'] / df['Total (GBP)'].values[-1])
    perc_col.append(100)
    df['%'] = perc_col

    # add percentage of funds in each curr
    perc_row = {}
    for col in df_cols:
        if col == 'Exchange':
            perc_row[col] = '%'
        else:
            perc_row[col] = 100 * df[col].values[-1] / df['Total (GBP)'].values[-1]
    perc_row['%'] = 100
    df = df.append(perc_row, ignore_index=True)

    # formatting and sorting
    df = df.loc[:, (df > 1).any(axis=0)]  # delete columns with less than £1 in
    df = df[:-3].sort_values(by='%', ascending=False).reset_index(drop=True).append(df[-3:], ignore_index=True)
    df = pd.concat(
        [df.iloc[:, 0], df.iloc[:, 1:-3].sort_values(by=len(df) - 1, ascending=False, axis=1), df.iloc[:, -3:]], axis=1)

    print(df)
    # profit calc
    if funds_invested is not None:
        current_value = df['Total (GBP)'].values[-2]
        profit = current_value - funds_invested
        profitperc = 100 * profit/funds_invested
        print('\nInvested: £{:.2f}, Current Value: £{:.2f}, Profit: £{:.2f}, {:+.2f}%'.format(
                funds_invested, current_value, profit, profitperc))

    if gbp_only:
        return df[['Exchange', 'Total (GBP)']][:-2]
    else:
        return df


def get_pair_data_list(client, use_checkpoint=False):
    checkpoint_path = os.path.join(CWD, 'checkpoints/pair_data_list_checkpoint.p')
    if use_checkpoint:
        with open(checkpoint_path, 'rb') as f:
            return pickle.load(f)
    markets = client.load_markets()
    pair_data_list = []
    for symbol, dd in markets.items():
        ticker = client.fetch_ticker(symbol)
        pair_data_list.append({
            'fsym': dd['base'],
            'tsym': dd['quote'],
            'price': ticker['last'],
            'symbol': symbol,
            'direction': 'buy',
            'exchange': client.name
        })
    pair_data_list = get_inv_pairs(pair_data_list)
    with open(checkpoint_path, 'wb') as f:
        pickle.dump(pair_data_list, f)
    return pair_data_list


def symbols_in_pair_data_list(pair_data_list):
    ''' List of unique symbols in pair_data_list '''
    return list(set([sublist for _list in [[d['tsym'], d['fsym']] for d in pair_data_list] for sublist in _list]))


def get_inv_pairs(pair_data_list):
    ''' For every trading pair in pair_data_list add the inverse pair, price, and direction '''
    pairs_inv = []
    for pair in pair_data_list:
        pair_inv = pair.copy()
        try:
            pair_inv['price'] = 1 / pair['price']
            pair_inv['fsym'] = pair['tsym']
            pair_inv['tsym'] = pair['fsym']
            pair_inv['direction'] = 'sell'
            pairs_inv.append(pair_inv)
        except ZeroDivisionError as e:
            pass
    pair_data_list = pair_data_list + pairs_inv
    return pair_data_list


def quick_buy(client, pair, funds, execute=False, amount_to_lots=False):
    """
    Make a limit buy just above the current bid price. Prints info.
    :param client: ccxt client
    :param pair: currency pair (e.g. 'BTC/EUR')
    :param funds: quote funds
    :param execute: safety param, set True to execute trade.
    :return: order info
    """

    tick = client.fetch_ticker(pair)
    bid = tick['bid']
    ask = tick['ask']
    mybid = int(tick['bid'] * 1.01 * 1e6) / 1e6
    amount = funds / mybid

    if amount_to_lots:
        amount = client.amount_to_lots(pair, amount)
    print(amount)

    if execute:
        order = client.create_order(pair, 'limit', 'buy', amount, price=mybid)
        return order
    else:
        return {'bid': mybid, 'amount': amount}


def quick_limit_order(client, pair, direction, fcurr_amount, execute=False, amount_to_lots=False):
    assert direction in {'buy', 'sell'}

    tick = client.fetch_ticker(pair)
    bid = tick['bid']
    ask = tick['ask']

    if direction == 'sell':
        mybid = tick['ask'] * 0.999
        amount = fcurr_amount  # fcurr_amount is the base currency amount
    elif direction == 'buy':
        mybid = tick['bid'] * 1.001
        amount = fcurr_amount / mybid  # fcurr_amount is in quote currency so calculate amount in base currency

    if amount_to_lots:
        amount = client.amount_to_lots(pair, amount)

    if execute:
        order = client.create_order(pair, 'limit', direction, amount, price=mybid)
        return order
    else:
        return {'bid': mybid, 'amount': amount}


def wait_for_fill(pair, client, id, timeout=60):
    """
    Waits for limit order to fill.
    :param pair: currency pair (e.g. BTC/LTC)
    :param client: ccxt client
    :param id: order id from ccxt order (e.g. order['id'])
    :param timeout: how long to wait - default is 10 minutes
    :return: will raise an error if it times out
    """
    for t in range(timeout):
        curr_order = client.fetch_order(id, pair)
        print('Status: {}, Fill amount: {}, Price: {}'.format(curr_order['status'], curr_order['filled'], curr_order['price']))
        if curr_order['status'] != 'open':
            return curr_order
        time.sleep(10)
    raise TimeoutError('Limit trade has not filled. Adjust order!')


def get_spread(base, quote, clients):
    """Returns spread for given pair for each client in clients."""
    spread = {}
    for c in clients:
        tick = c.fetch_ticker(base + '/' + quote)
        spread[c.describe()['name']] = {'bid': tick['bid'], 'ask': tick['ask']}
    return spread


def calc_market_price(base, quote, amount, client):
    """ Calculates price of market order based on current depth """
    order_book = client.fetch_order_book(base + '/' + quote)
    for side in ['asks', 'bids']:
        fill, cost = 0, 0
        depth = order_book[side]
        while fill < amount:
            for order in depth:
                delta = min(order[1], (amount - fill))
                cost += order[0] * delta
                fill += delta
        assert fill == amount, 'fill: {}, amount: {}'.format(fill, amount)
        if side == 'asks':
            buy_price = cost / fill
        else:
            sell_price = cost / fill

    return buy_price, sell_price


def find_trade_paths(fcurr, tcurr, pair_data_list, limit_route_len=None, verbose=False):
    """
    :param pair_data_list: output from get_pair_data_list
    """
    start_pairs = pairs_with_tsym(fcurr, pair_data_list)
    if verbose:
        print(start_pairs)
    routes = [[pair] for pair in start_pairs]  # Starting pairs form the beginning of each route
    routes = extend_trade_routes(routes, tcurr, pair_data_list)  # Recursively extend routes until fsym = tcurr for each route
    if verbose:
        print(list(routes))
    if limit_route_len:
        routes = [route for route in routes if len(route) <= limit_route_len]
    return routes


def extend_trade_routes(routes, end_fsym, pair_data_list):
    """
    Recurivsely extend routes until 'fsym' = 'end_fsym' for each route
    :param routes: list of route chains to be extended until end_fsym is reached
    :param end_fsym: the fsym signaling the chain is complete
    :param pair_data_list: list of dicts which must have values for 'fsym' and 'tsym'
    :yield: each complete route as a list of dicts
    """
    for route in routes:
        if len(route) > 3:  # More than this can take a long time
            pass
        else:
            last_fsym = route[-1]['fsym']
            if last_fsym == end_fsym:  # Route complete
                yield route
            else:
                linking_pairs = pairs_with_tsym(last_fsym, pair_data_list)
                linking_pairs = [pair for pair in linking_pairs if pair not in route]  # Prevent circling
                new_chains = [route + [pair] for pair in linking_pairs]
                yield from extend_trade_routes(new_chains, end_fsym, pair_data_list)


def trade_path_outcomes(route, in_amount, fee_perc):
    """
    Calculate outcomes for each trade in the route
    :param route: list of pairs. assume that we're selling tsym and buying fsym for each pair
    :param in_amount: amount of currency in terms of the starting tsym
    :return: list of amounts corresponding to each pair in the route, where the last element is the end result
    """
    def inv(x):
        try:
            return 1 / float(x)
        except ZeroDivisionError as e:
            return np.nan
    fee_coeff = 1 - fee_perc
    new_amount = (in_amount * fee_coeff) * inv(route[0]['price'])  # Outcome for first pair
    out_amounts = [new_amount]
    if len(route) > 1:
        for pair in route[1:]:
            new_amount = (new_amount * fee_coeff) * inv(pair['price'])
            out_amounts.append(new_amount)
    return out_amounts


def best_trade_path(routes, in_amount=1, fee_perc=0.03):
    """
    :return: best route (list of trading pair dicts), predicted outcome amount
    """
    best_route = None
    highest_outcome = 0
    for route in routes:
        trade_outcomes = trade_path_outcomes(route, in_amount=in_amount, fee_perc=fee_perc)
        final_amount = trade_outcomes[-1]  # Outcome of the last trade
        if final_amount > highest_outcome or (final_amount == highest_outcome and len(route) < len(best_route)):
            best_route, highest_outcome = route, final_amount
    return best_route, highest_outcome


def shortest_path(routes):
    try:
        return sorted(routes, key=lambda x: len(x))[0]
    except:
        return None


def pairs_with_tsym(sym, pair_data_list):
    return [pair for pair in pair_data_list if sym == pair['tsym']]


if __name__ == '__main__':
    pass
    # cmc = Market()
    # print(cmc.ticker('Litecoin'))
