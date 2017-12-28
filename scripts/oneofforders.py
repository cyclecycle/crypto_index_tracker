from private import CLIENTS, ADDRESSES
from prices.snapshots import compare_two_exchanges_ccxt
import ccxt
import time


if __name__ == '__main__':
    quick_buy(CLIENTS['Binance'], 'REQ/ETH', 0.5, execute=True)
