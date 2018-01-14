from private import CLIENTS
from prices.snapshots import compare_order_books, get_single_price, compare_actual_market_prices
from trade.util import quick_buy, wait_for_fill
import pickle

if __name__ == '__main__':
    GDAX = CLIENTS['GDAX']
    kucoin = CLIENTS['Kucoin']
    binance = CLIENTS['Binance']
    # print(compare_order_books(['ETH', 'LTC'], 'BTC', GDAX, kucoin))
    #
    # gdax_ltceth = get_single_price('LTC', 'BTC', 'GDAX', ret_float=True) / get_single_price('ETH', 'BTC', 'GDAX', ret_float=True)
    # kucoin_ltceth = kucoin.fetch_ticker('LTC/ETH')['ask']
    #
    # print((kucoin_ltceth/gdax_ltceth - 1) * 100)
    #
    # bal = kucoin.fetch_balance()['ETH']
    # print(bal)
    # # order = quick_buy(kucoin, 'LTC/ETH', 0.4, execute=True)
    # # print(order)
    # # print(wait_for_fill('LTC/ETH', kucoin, order['id']))

    # print(compare_actual_market_prices('NEO', 'ETH', 1000, (binance, kucoin)))

    ob = binance.fetch_order_book('NEO/ETH')

    print(ob)
    ob = pickle.load(open('test.p', 'ab'))
    print(ob)