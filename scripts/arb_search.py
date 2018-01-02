from prices.snapshots import *
from prices.historical import historical_compare
from prices.trackers import CompareTwoExchangesTracker
from prices.util import filter_unlisted_pairs
import pandas as pd
import matplotlib.pyplot as plt

BITFINEX_BINANCE_ETH_BASES = ['IOT', 'EOS', 'BCH', 'NEO', 'OMG']
GATECOIN_BINANCE_ETH_BASES = ['LTC', 'TRX', 'ZRX', 'CDT', 'ADX']
KUCOIN_BINANCE_ETH_BASES = ['KNC', 'VEN', 'HSR', 'MTH', 'BCH', 'EVX', 'OMG', 'BCD', 'GVT', 'REQ', 'BTG', 'MOD', 'SUB', 'PPT', 'BCPT', 'NULS', 'QSP']
KRAKEN_BINANCE_ETH_BASES = ['EOS', 'ETC', 'ICN']
KRAKEN_BITSTAMP_BTC_BASES = ['XRP', 'BCH', 'LTC']
KRAKEN_BITSTAMP_EUR_BASES = ['XRP', 'BCH', 'LTC', 'ETH', 'BTC']
KRAKEN_GDAX_EUR_BASES = ['BTC', 'ETH', 'LTC']

if __name__ == '__main__':
    print(compare_two_exchanges(KUCOIN_BINANCE_ETH_BASES, 'ETH', 'Kucoin', 'Binance'))
    # print(compare_two_exchanges(GATECOIN_BINANCE_ETH_BASES, 'ETH', 'Gatecoin', 'Binance'))
    # print(compare_two_exchanges(KRAKEN_BINANCE_ETH_BASES, 'ETH', 'Kraken', 'Binance'))
    # # track = CompareTwoExchangesTracker(log_filename='krakenarb.csv', num_snaps=180, interval=10)
    # # track.track(KRAKEN_BINANCE_ETH_BASES, 'ETH', 'Kraken', 'Binance')
    # # track.plot()
    # #
    # # print(historical_compare(KRAKEN_BINANCE_ETH_BASES, 'ETH', 'Kraken', 'Binance'))
    # # print(compare_two_exchanges('LTC', 'BTC', 'GDAX', 'Bitstamp'))
    #
    # # print(compare_two_exchanges(KRAKEN_BITSTAMP_EUR_BASES, 'EUR', 'Kraken', 'Bitstamp'))
    # # print(compare_two_exchanges(KRAKEN_GDAX_EUR_BASES, 'EUR', 'Kraken', 'GDAX'))
    #
    # # print(historical_compare(KRAKEN_BITSTAMP_EUR_BASES, 'EUR', 'Kraken', 'Bitstamp'))
    #
    track = CompareTwoExchangesTracker(log_filename='kucoinarb.csv', num_snaps=180, interval=10)
    # track.track(KUCOIN_BINANCE_ETH_BASES, 'ETH', 'Kucoin', 'Binance')
    # track.plot()

    track.load_csv()
    viable_pairs = []
    for col in track.df:
        if '0' not in col:
            flag = True
            for val in track.df[col].values:
                if abs(val) < 1:
                    flag = False
            if flag:
                viable_pairs.append(col)

    track.df = track.df[viable_pairs]
    track.plot()


    # print([p[:-4] for p in filter_unlisted_pairs(KUCOIN_BINANCE_ETH_BASES, 'ETH', 'Binance')])