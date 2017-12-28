from private import CLIENTS, ADDRESSES
from prices.snapshots import compare_two_exchanges_ccxt
import ccxt
import time

def kraken_binance_ETC_ETH(eth_in_binance):
    """
    ETC tends to be 1-2% cheaper on Kraken than Binance.
    Need ~equivalent amount of ETC in Kraken as ETH in Binance for simultaneous trade.
    """
    kraken = CLIENTS['Kraken']
    binance = CLIENTS['Binance']

    flag = False
    undercut = 0.001
    while not flag:
        pdict, mpd = compare_two_exchanges_ccxt('ETC', 'ETH', kraken, binance)
        # print(pdict)
        print('Min % diff: {}'.format(mpd))

        bid = pdict['Binance']['ask'] * (1 - undercut)
        ask = pdict['Kraken']['bid'] * (1 + undercut)

        withdrawal_fees = (kraken.describe()['fees']['funding']['withdraw']['ETH'],
                           binance.describe()['fees']['funding']['withdraw']['ETC'])
        taker_fees = (kraken.describe()['fees']['trading']['taker'], binance.describe()['fees']['trading']['taker'])
        # taker_fees = (taker_fees[0], 0)
        estimated_min_gain = (eth_in_binance * ((1 - taker_fees[1]) / bid) - withdrawal_fees[1]) * \
                             ask * (1 - taker_fees[0]) - withdrawal_fees[0] - eth_in_binance

        print('Min Gain: {}'.format(estimated_min_gain))
        print('Binance ask: {:.5f}, My bid: {:.5f}, Binance bid: {:.5f}'.format(
            pdict['Binance']['ask'], bid, pdict['Binance']['bid']))
        print('Kraken ask: {:.5f}, My ask: {:.5f}, Kraken bid: {:.5f}'.format(
            pdict['Kraken']['ask'], ask, pdict['Kraken']['bid']))

        if bid < pdict['Binance']['bid'] or ask > pdict['Kraken']['ask']:
            print('FAIL')
            flag = True
        elif estimated_min_gain > 0:
            print('SUCCCESS')
            flag = True
        else:
            time.sleep(5)
            undercut += 0.001


if __name__ == '__main__':
    kraken_binance_ETC_ETH(eth_in_binance=2)