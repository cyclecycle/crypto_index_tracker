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


def build_trade_routes(fcurr, tcurr, pair_data_list, limit_route_len=None):
    start_pairs = pairs_with_tsym(fcurr, pair_data_list)
    routes = [[pair] for pair in start_pairs]  # Starting pairs form the beginning of each route
    routes = extend_trade_routes(routes, tcurr, pair_data_list)  # Recursively extend routes until fsym = tcurr for each route
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
        for pair in route:
            fsym = pair['fsym']
            if fsym == end_fsym:  # Route complete
                yield route
            else:
                linking_pairs = pairs_with_tsym(fsym, pair_data_list)
                new_chains = [route.append(pair) for pair in linking_pairs]
                build_trade_routes(new_chains, end_fsym, pair_data_list)


def trade_route_outcomes(route, in_amount, fee_perc=0.03):
    """
    Calculate outcome of a trading route
    :param route: list of pairs. assume that we're tsym and buying fsym for each pair.
    :param in_amount: amount of currency in terms of the starting tsym
    :return: list of amounts corresponding to each pair in the route, where the last element is the end result.
    """
    fee_coeff = 1 - fee_perc
    new_amount = (in_amount * fee_coeff) * (1 / route[0]['price'])  # Outcome for first pair
    out_amounts = [new_amount]
    if len(route) > 1:
        for pair in route[1:]:
            new_amount = (new_amount * fee_coeff) * (1 / float(pair['price']))
            out_amounts.append(new_amount)
    return out_amounts


def best_trading_route(routes, in_amount=100):
    """
    :param pair2price: list of dicts containing currency pairs and prices
    :param fcurr: currency to be sold
    :param in_amount: amount of fcurr to be sold
    :param tcurr: currency to be maximised
    :return: best route (list of trading pairs), predicted in_amount
    """
    best_route = None
    highest_outcome = 0
    for route in routes:
        trade_outcomes = trade_route_outcomes(route, in_amount)
        final_amount = trade_outcomes[-1]  # Outcome of the last trade
        if final_amount > highest_outcome or (final_amount == highest_outcome and len(route) < len(best_route)):
            best_route, highest_outcome = route, final_amount
    return best_route, highest_outcome


''' Convenience functions '''

def pairs_with_tsym(sym, pair_data_list):
    return [pair for pair in pair_data_list if sym == pair['tsym']]


if __name__ == '__main__':
    pair_data_list = [
        {
            'fsym': 'BTC',
            'tsym': 'EUR',
            'price': 12757
        },
        {
            'fsym': 'ETH',
            'tsym': 'EUR',
            'price': 689
        },
        {
            'fsym': 'ETH',
            'tsym': 'BTC',
            'price': 0.05
        }
    ]
    routes = build_trade_routes('EUR', 'ETH', pair_data_list)
    route, amount = best_trading_route(routes, in_amount=2000)  # Pass amount in start currency, receive amount in target currency
    print(route, amount)