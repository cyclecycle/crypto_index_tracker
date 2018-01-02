from private import CLIENTS, ADDRESSES
from prices.snapshots import compare_two_exchanges_ccxt
import ccxt
import time

def single_arb_pair_check(base, quote, funds, clients, seperate_taker_fees=False):
    """
    Checks arb gain for single currency pair. This function models buying the base coin on the
    cheaper exchange and selling it on the more expensive one. It aims to hold the base constant
    and increase the amount of the quote coin (usually ETH). The trade is exectuted by simulataneously
    placing limit orders on both exchanges which undercut the current bid/ask price. The extent of this
    undercut will be increased from the worst possible price to the other end of the spread until
    a positive minimum gain is achieved.
    :param base: base coin (the amount of this coin will be held constant)
    :param quote: quote coin (this coin will increase by the arb gain)
    :param funds: initial amount of quote coin
    :param clients: tuple of ccxt clients
    :param seperate_taker_fees: if True will pay taker fees with other funds and remove from total gain
    :return check: a bool with the result of the check (True = pass)
    :return buy_name: str of the client to buy from
    :return undercut: value of undercut for check to pass (None if all values within spread fail)
    """

    undercut = 0.001

    while True:

        pdict, mpd = compare_two_exchanges_ccxt(base, quote, *clients)
        # print(pdict)

        buy_idx = 0 if mpd < 0 else 1
        buy_name = clients[buy_idx].describe()['name']
        sell_name = clients[1 - buy_idx].describe()['name']

        print('Min % diff: {}'.format(mpd))

        bid = pdict[buy_name]['ask'] * (1 - undercut)
        ask = pdict[sell_name]['bid'] * (1 + undercut)

        withdrawal_fees = (clients[buy_idx].describe()['fees']['funding']['withdraw'][quote],
                           clients[1 - buy_idx].describe()['fees']['funding']['withdraw'][base])

        taker_fees = (clients[buy_idx].describe()['fees']['trading']['taker'],
                      clients[1 - buy_idx].describe()['fees']['trading']['taker'])
        taker_fee_coeff = 1
        if seperate_taker_fees:
            # taker fees taken out of equation and applied as coefficient of final value
            taker_fee_coeff = 1 - sum(taker_fees) / 2
            taker_fees = (0, 0)

        estimated_min_gain = (funds * (((1 - taker_fees[0]) / bid) - withdrawal_fees[0]) *
                              ask * (1 - taker_fees[1]) - withdrawal_fees[1]) * taker_fee_coeff - funds

        print('Min Gain: {}'.format(estimated_min_gain))
        print('{} ask: {:.5f}, My bid: {:.5f}, {} bid: {:.5f}'.format(
            buy_name, pdict[buy_name]['ask'], bid, buy_name, pdict[buy_name]['bid']))
        print('{} ask: {:.5f}, My ask: {:.5f}, {} bid: {:.5f}'.format(
            sell_name, pdict[sell_name]['ask'], ask, sell_name, pdict[sell_name]['bid']))

        if bid < pdict[buy_name]['bid'] or ask > pdict[sell_name]['ask']:
            check = False
            undercut = None
            return check, buy_name, undercut
        elif estimated_min_gain > 0:
            check = True
            return check, buy_name, undercut
        else:
            time.sleep(5)
            undercut += 0.001


if __name__ == '__main__':
    print(single_arb_pair_check('LTC', 'BTC', 2, (CLIENTS['GDAX'], CLIENTS['Kraken'])))