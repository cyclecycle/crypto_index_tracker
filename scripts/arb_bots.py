from private import CLIENTS, ADDRESSES
from prices.snapshots import compare_two_exchanges_ccxt
import ccxt
import time


def min_gain_calc(base, quote, funds, client1, client2):

    flag = False
    undercut = 0.001
    while not flag:
        pdict, mpd = compare_two_exchanges_ccxt(base, quote, client1, client2)
        # print(pdict)

        buy = 1 if mpd < 0 else 2
        print('Min % diff: {}'.format(mpd))

        bid = pdict['Binance']['ask'] * (1 - undercut)
        ask = pdict['Kraken']['bid'] * (1 + undercut)

        withdrawal_fees = (client1.describe()['fees']['funding']['withdraw'][quote],
                           client2.describe()['fees']['funding']['withdraw'][base])
        taker_fees = (client1.describe()['fees']['trading']['taker'], client2.describe()['fees']['trading']['taker'])
        # taker_fees = (taker_fees[0], 0)
        estimated_min_gain = (funds * ((1 - taker_fees[1]) / bid) - withdrawal_fees[1]) * \
                             ask * (1 - taker_fees[0]) - withdrawal_fees[0] - funds

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
    min_gain_calc('LTC', 'ETH', 2, CLIENTS['Kraken'], CLIENTS['GDAX'])