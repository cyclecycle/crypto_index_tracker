from private import CLIENTS, ADDRESSES
from prices.snapshots import compare_two_exchanges_ccxt
from trade.util import quick_buy
import ccxt
import time


if __name__ == '__main__':
    # print(quick_buy(CLIENTS['Kraken'], 'VEN/ETH', 0.7, execute=True))
    kraken = CLIENTS['Kraken']
    print(kraken.withdraw('ETH', 0.9, '0xb244fc9f7e18fe6aeb6db0aa3ec65a5761aa73ca', params={'key': 'BINANCE ETH'}))