# from bots import CoreBot

# class Optimiser(CoreBot):
#     """
#     Use variables ranges defined in rule set to test parameter combinations on historical data and return the rule set config that
#     optimises the output
#     """

#     def __init__(self, output):
#         """
#         :output: the observable to maximise
#         """


def best_trading_route(pair_data_list, fcurr, amount, tcurr, fee_coeff=0.03, route_limit_len=3):
    """
    :param pair2price: list of dicts containing currency pairs and prices
    :param fcurr: currency to be sold
    :param amount: amount of fcurr to be sold
    :param tcurr: currency to be maximised
    :return: list of trades to be made
    """

    def pairs_with_tsym(sym, pair_data_list):
        return [pair for pair in pair_data_list if sym == pair['tsym']]

    def build_routes(end_fsym, routes):
        """
        Recurivsely generate lists of pairs until fsym == end_fsym
        :param end_fsym: the fsym signaling the last pair in the chain
        :param routes: list of incomplete route chains
        :yield: complete routes
        """
        for route in routes:
            for pair in route:
                fsym = pair['fsym']
                if fsym == end_fsym:  # Route route complete
                    yield route
                else:
                    linking_pairs = pairs_with_tsym(fsym, pair_data_list)
                    new_chains = [route.append(pair) for pair in linking_pairs]
                    build_routes(end_fsym, new_chains)

    start_pairs = pairs_with_tsym(fcurr, pair_data_list)
    routes = [[pair] for pair in start_pairs]  # Start pairs form the beginning of each route
    routes = build_routes(tcurr, routes)
    print(list(routes))

    # ''' Calculate outcome amount for each route '''
    # route_outcomes = []
    # for route in routes:
    #     amount = route[0]['']
    #     for pair in route:
    #         print(pair)
    #         fsym_amount = last_amount * 1 / float(pair['price'])
    #         print(fsym_amount)
    #         route_outcomes.append(outcome)
    # print(route_outcomes)

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
    best_trading_route(pair_data_list, 'ETH', 2000, 'ETH')