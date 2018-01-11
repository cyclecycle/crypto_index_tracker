from prices.snapshots import *
from prices.historical import historical_compare
from prices.trackers import CompareTwoExchangesTracker, CompareOrderBooksTracker
from prices.util import filter_unlisted_pairs
import pandas as pd
import ccxt
import matplotlib.pyplot as plt
from private import CLIENTS

BITFINEX_BINANCE_ETH_BASES = ['IOT', 'EOS', 'BCH', 'NEO', 'OMG']
GATECOIN_BINANCE_ETH_BASES = ['LTC', 'TRX', 'ZRX', 'CDT', 'ADX']
KUCOIN_BINANCE_ETH_BASES = ['NEO', 'KNC', 'VEN', 'HSR', 'MTH', 'BCH', 'EVX', 'OMG', 'BCD', 'GVT', 'REQ', 'BTG', 'MOD', 'SUB', 'PPT', 'BCPT', 'NULS', 'QSP']
SAFE_KUCOIN_BINANCE_ETH_BASES = ['NEO', 'KNC', 'VEN', 'BCH', 'OMG', 'REQ', 'MOD', 'LTC']
KRAKEN_BINANCE_ETH_BASES = ['EOS', 'ETC', 'ICN']
KRAKEN_BITSTAMP_BTC_BASES = ['XRP', 'BCH', 'LTC']
KRAKEN_BITSTAMP_EUR_BASES = ['XRP', 'BCH', 'LTC', 'ETH', 'BTC']
KRAKEN_GDAX_EUR_BASES = ['BTC', 'ETH', 'LTC']

if __name__ == '__main__':
    clients = (CLIENTS['Binance'], CLIENTS['Kucoin'])
    print(compare_order_books(SAFE_KUCOIN_BINANCE_ETH_BASES, 'ETH', (CLIENTS['Binance'], CLIENTS['Kucoin'], ccxt.gatecoin())))


    # print(compare_order_books('NEO', 'ETH', clients))

    # tracker = CompareOrderBooksTracker(log_filename='modeth.csv', num_snaps=120, interval=10)
    # tracker.track('MOD', 'ETH', clients)
    # tracker.plot()

    # tracker.load_csv()
    # tracker.plot()

    # track = CompareTwoExchangesTracker(log_filename='kucoinarb.csv', num_snaps=180, interval=10)
    #
    # track.load_csv()
    # viable_pairs = []
    # for col in track.df:
    #     if '0' not in col:
    #         flag = True
    #         for val in track.df[col].values:
    #             if abs(val) < 1:
    #                 flag = False
    #         if flag:
    #             viable_pairs.append(col)
    #
    # track.df = track.df[viable_pairs]
    # track.plot()


    # print([p[:-4] for p in filter_unlisted_pairs(KUCOIN_BINANCE_ETH_BASES, 'ETH', 'Binance')])