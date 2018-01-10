from private import CLIENTS, ADDRESSES
import ccxt
import time

# kraken = CLIENTS['Kraken']
# binance = CLIENTS['Binance']





# print([mar['symbol'] for mar in kraken.fetch_markets()])
#
# print(kraken.create_order('XMR/EUR', 'limit', 'sell', 0.1, price=400))


# gdax.withdraw('LTC', 2.5, ADDRESSES['Binance']['LTC'], params={'two_factor_code': 511842})

# print(binance.fetch_balance()['ETH'])
# print([mar['symbol'] for mar in binance.fetch_markets()])

# b_tick = binance.fetch_ticker('ETC/ETH')
# k_tick = kraken.fetch_ticker('ETC/ETH')
#
# print('Binance: ask - {}, bid - {}'.format(b_tick['ask'], b_tick['bid']))
# print('Kraken: ask - {}, bid - {}'.format(k_tick['ask'], k_tick['bid']))
#
# gain = 100 * k_tick['ask']/b_tick['bid'] - 100
# print("diff: {}%".format(gain))
#
# if gain > 1:
#


# b_tick = binance.fetch_ticker('ETC/ETH')
# k_tick = kraken.fetch_ticker('ETC/ETH')
#
# print('Binance: ask - {}, bid - {}'.format(b_tick['ask'], b_tick['bid']))
# print('Kraken: ask - {}, bid - {}'.format(k_tick['ask'], k_tick['bid']))
#
# gain = 100 * k_tick['ask'] / b_tick['bid'] - 100
# print("diff: {}%".format(gain))
#
# if gain > 1:
#
#     b_tick = binance.fetch_ticker('ETC/ETH')
#     print(b_tick['bid'], b_tick['ask'])
#     bidprice = b_tick['ask']*0.999
#     print(1/bidprice)
#     order = binance.create_order('ETC/ETH', 'limit', 'buy', 1/bidprice, price=bidprice)
#     print(order)
#
#     openflag = True
#     while openflag == True:
#         time.sleep(10)
#         curr_order = binance.fetch_order(order['id'], 'ETC/ETH')
#         print(curr_order['status'], curr_order['filled'], curr_order['price'])
#         if curr_order['status'] != 'open':
#             openflag = False


# bal = binance.fetch_balance()['ETC']['total']
# print(bal)
# print(binance.withdraw('ETC', bal, ADDRESSES['Kraken']['ETC']))

# bal = kraken.fetch_balance()['ETH']['total']
# print(bal)
# print(kraken.withdraw('ETH', bal, ADDRESSES['Binance']['ETH'], params={'key': 'BINANCE ETH'}))
