from prices.snapshots import *
from prices.trackers import compare_two_exchanges_tracker
import pandas as pd
import matplotlib.pyplot as plt

BITFINEX_BINANCE_ETH_BASES = ['IOT', 'EOS', 'BCH', 'NEO', 'OMG']
GATECOIN_BINANCE_ETH_BASES = ['LTC', 'TRX', 'ZRX', 'CDT', 'ADX']
KRAKEN_BINANCE_ETH_BASES = ['EOS', 'ETC', 'ICN']

if __name__ == '__main__':

    # print(compare_two_exchanges(GATECOIN_BINANCE_ETH_BASES, 'ETH', 'Gatecoin', 'Binance'))
    print(compare_two_exchanges(KRAKEN_BINANCE_ETH_BASES, 'ETH', 'Kraken', 'Binance'))


    df = pd.read_csv('krakenarb.csv')
    plt.plot(df.iloc[0].values)
    plt.plot(df.iloc[1].values)
    plt.plot(df.iloc[2].values)

    plt.xlabel('minute')
    plt.ylabel('% difference')
    plt.show()


