from prices.snapshots import *
from prices.historical import historical_compare
import pandas as pd
import matplotlib.pyplot as plt

BITFINEX_BINANCE_ETH_BASES = ['IOT', 'EOS', 'BCH', 'NEO', 'OMG']
GATECOIN_BINANCE_ETH_BASES = ['LTC', 'TRX', 'ZRX', 'CDT', 'ADX']
KRAKEN_BINANCE_ETH_BASES = ['EOS', 'ETC', 'ICN']


if __name__ == '__main__':

    # print(compare_two_exchanges(GATECOIN_BINANCE_ETH_BASES, 'ETH', 'Gatecoin', 'Binance'))
    # print(compare_two_exchanges(KRAKEN_BINANCE_ETH_BASES, 'ETH', 'Kraken', 'Binance'))
    #
    # print(historical_compare(KRAKEN_BINANCE_ETH_BASES, 'ETH', 'Kraken', 'Binance'))
    print(compare_two_exchanges('LTC', 'BTC', 'GDAX', 'Bitstamp'))