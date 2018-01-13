from private import CLIENTS, ADDRESSES
from trade.util import quick_buy, wait_for_fill
import ccxt
import time


if __name__ == '__main__':
    # print(quick_buy(CLIENTS['Kraken'], 'VEN/ETH', 0.7, execute=True))
    kraken = CLIENTS['Kraken']
    binance = CLIENTS['Binance']
    GDAX = CLIENTS['GDAX']
    kucoin = CLIENTS['Kucoin']
    # order = quick_buy(binance, 'BCH/ETH', 0.5, execute=True)
    # print(order['id'])
    # wait_for_fill('BCH/ETH', binance, order['id'])

    # GDAX.withdraw('ETH', 0.02, '0x13DAF8C05EF3F9da8Ad21fc1D73Aa4C2712983Cb', {'two_factor_code': 552858})
    # quick_buy(kraken, 'ETH/EUR', 2000, execute=True)
    # print(kraken.withdraw('ETH', 2.2, '0xb244fc9f7e18fe6aeb6db0aa3ec65a5761aa73ca', params={'key': 'BINANCE ETH'}))


    # bal = binance.fetch_balance()
    # print(bal['ETH'], bal['BNB'])
    # ask = binance.fetch_ticker('LTC/ETH')['ask']
    # # ask = binance.fetch_ticker('LTC/BNB')['ask']
    # amount = 0.1/ask
    # order = binance.create_order('BNB/ETH', 'market', 'buy', amount)
    # print(order)
    # order = wait_for_fill('BNB/ETH', binance, order['id'])
    #
    # print(order)
    # bal = binance.fetch_balance()
    # print(bal['ETH'], bal['BNB'])


    # bal = binance.fetch_balance()
    # print(bal['ETH'])

    # quick_buy(kraken, 'XMR/EUR', 728, execute=True)
    # kraken.create_order('ETH/EUR', 'limit', 'buy', 1, price=1000)
    # quick_buy(kucoin, 'BNTY/ETH', 1, execute=True)
    # kraken.withdraw('ETH', 2, '0xb244fc9f7e18fe6aeb6db0aa3ec65a5761aa73ca', params={'key': 'BINANCE ETH'})
    # print(binance.fetch_order('10432418', symbol='BNB/ETH'))

    order = quick_buy(binance, 'VEN/ETH', 0.53, execute=True)
    # print(order)
    # print(wait_for_fill('KCS/ETH', kucoin, order['id']))
    # orders = kucoin.fetch_trades('KCS/ETH')
    # print(orders)
    # print(kraken.fetch_balance()['ETH'])
    # print(quick_buy(kraken, 'ETH/EUR', 2000, execute=True))
    # print(binance.fetch_order_book('NEO/ETH'))

    # print(binance.withdraw('NEO', int(amount), 'AHckMs2PWojV6D3SKRrGmHMkwQCt15Egdm'))