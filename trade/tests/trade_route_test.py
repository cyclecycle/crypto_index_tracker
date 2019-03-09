import pickle
import util


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

# with open('tests/pair_data_list_checkpoint.p', 'wb') as f:
#     pickle.dump(pair_data_list, f)

with open('tests/pair_data_list_checkpoint.p', 'rb') as f:
    pair_data_list = pickle.load(f)


# routes = find_trade_paths('EUR', 'XRP', pair_data_list)
# assert len(list(routes)) == 0  # No EUR pairs in binance

# routes = find_trade_paths('ETH', 'ETH', pair_data_list)
# route, amount = best_trade_path(routes, in_amount=1, fee_perc=0.005)  # Pass amount in start currency, receive amount in target currency
# print(route, amount)
