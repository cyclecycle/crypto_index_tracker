# from bots import CoreBot

# class BotOptimiser(CoreBot):
#     """
#     Use variables ranges defined in rule set to test parameter combinations on historical data and return the rule set config that
#     optimises the output
#     """

#     def __init__(self, output):
#         """
#         :output: the observable to maximise
#         """

import os
from pathlib import Path
import numpy as np
import ccxt
import yaml
import util


ROOT = Path(os.path.dirname(os.path.realpath(__file__))).parents[0]
with open(os.path.join(ROOT, 'trade/api_keys.yaml')) as f:
    API_KEYS = yaml.load(f)


def find_trade_paths(fcurr, tcurr, pair_data_list, limit_route_len=None, verbose=False):
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


''' Convenience functions '''

def pairs_with_tsym(sym, pair_data_list):
    return [pair for pair in pair_data_list if sym == pair['tsym']]


if __name__ == '__main__':
    # pair_data_list = [
    #     {
    #         'fsym': 'BTC',
    #         'tsym': 'EUR',
    #         'price': 12757
    #     },
    #     {
    #         'fsym': 'ETH',
    #         'tsym': 'EUR',
    #         'price': 689
    #     },
    #     {
    #         'fsym': 'ETH',
    #         'tsym': 'BTC',
    #         'price': 0.05
    #     },
    #     {
    #         'fsym': 'ETH',
    #         'tsym': 'XLM',
    #         'price': 0.05
    #     },
    #     {
    #         'fsym': 'XRP',
    #         'tsym': 'ETH',
    #         'price': 0.05
    #     }
    # ]
    # pair_data_list = util.get_inv_pairs(pair_data_list)


    ''' Tests TODO move into separate file '''
    # binance = ccxt.binance(API_KEYS['BINANCE'])
    # pair_data_list = util.get_pair_data_list(binance)
    import pickle
    # with open('tests/pair_data_list_checkpoint.p', 'wb') as f:
    #     pickle.dump(pair_data_list, f)

    with open('tests/pair_data_list_checkpoint.p', 'rb') as f:
        pair_data_list = pickle.load(f)


    # routes = find_trade_paths('EUR', 'XRP', pair_data_list)
    # assert len(list(routes)) == 0  # No EUR pairs in binance

    # routes = find_trade_paths('ETH', 'ETH', pair_data_list)
    # route, amount = best_trade_path(routes, in_amount=1, fee_perc=0.005)  # Pass amount in start currency, receive amount in target currency
    # print(route, amount)
