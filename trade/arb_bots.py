from private import CLIENTS, ADDRESSES
from trade.util import wait_for_fill, get_spread, calc_market_price
from prices.snapshots import compare_order_books
import ccxt
import time
from datetime import datetime


# from tests.util import TESTCLIENTS, t_compare_two_exchanges_ccxt


class ArbPairBot:
    """
    Arb for single currency pair on 2 exchanges. We aim to hold the base constant and increase the amount of the quote
    coin (usually ETH). Trades are executed by simultaneously placing limit orders on both exchanges which undercut the
    current bid/ask price.
    """

    def __init__(self, base, quote, buy_client, sell_client, funds=1, seperate_taker_fees=False, min_gain_threshold=0, market_orders=False):
        self.base = base  # base coin (the amount of this coin will be held constant)
        self.quote = quote  # quote coin (this coin will increase by the arb gain)
        self.pair = base + '/' + quote

        self.buy_ex = get_client_info(buy_client, withdraw_coin=base)
        self.sell_ex = get_client_info(sell_client, withdraw_coin=quote)

        self.funds = funds  # initial amount of quote coin
        self.sep_fees = seperate_taker_fees  # if True will pay taker fees with other funds and remove from total gain
        self.thresh = min_gain_threshold  # optional threshold for gain (in funds units)
        self.market_orders = market_orders  # if True, will trade with market orders

        self.offset = 0.001  # fractional offset to bid/ask price (where 0 is market order)
        self.ask = None
        self.bid = None

    def check(self):
        """ Check for suitable gain with current tickers """
        self.offset = 0.001
        while True:
            # this is ugly - do we need get_spread as a function? leave it for now
            spread = get_spread(self.base, self.quote, (self.buy_ex['client'], self.sell_ex['client']))
            self.buy_ex['bid'], self.buy_ex['ask'] = spread[self.buy_ex['name']]['bid'], spread[self.buy_ex['name']]['ask']
            self.sell_ex['bid'], self.sell_ex['ask'] = spread[self.sell_ex['name']]['bid'], spread[self.sell_ex['name']]['ask']

            mpd = 100 * (self.sell_ex['bid'] / self.buy_ex['ask'] - 1)
            print('Min % diff: {}'.format(mpd))

            if not self.market_orders:
                bid, ask = self.buy_ex['ask'] * (1 - self.offset), self.sell_ex['bid'] * (1 + self.offset)
            else:
                bid, ask = self.buy_ex['ask'], self.sell_ex['bid']

            if self.sep_fees:
                # taker fees taken out of equation and applied as coefficient of final value
                tfee = (self.buy_ex['tfee'] + self.sell_ex['tfee']) / 2
                est_min_gain = self.funds * (
                        ((1 / bid - self.buy_ex['wfee']) * ask - self.sell_ex['wfee']) * (1 - tfee) - 1)
            else:
                est_min_gain = self.funds * (((1 - self.buy_ex['tfee']) / bid - self.buy_ex['wfee']) *
                                             ask * (1 - self.buy_ex['tfee']) - self.sell_ex['wfee'] - 1)

            print('Min Gain: {}'.format(est_min_gain))

            if self.market_orders:
                print(spread)
                return True if est_min_gain > 0 else False
            elif bid < spread[self.buy_ex['name']]['bid'] or ask > spread[self.sell_ex['name']]['ask']:
                return False
            elif est_min_gain > self.thresh:
                print(spread)
                print('my ask: {:.5f}, My bid: {:.5f}'.format(ask, bid))
                self.ask, self.bid = ask, bid
                return True
            else:
                time.sleep(5)
                self.offset += 0.001

    def trade(self, wait=True):
        """ Execute trade. If wait, will wait for each order to fill. """
        check = self.check()
        if not check:
            return

        if self.market_orders:
            order = self.buy_ex['client'].create_order(self.pair, 'market', 'buy', 1 / self.bid)
            self.buy_ex['order id history'].append(order['id'])
            order = self.sell_ex['client'].create_order(self.pair, 'market', 'sell', 1 / self.bid)
            self.sell_ex['order id history'].append(order['id'])

        order = self.buy_ex['client'].create_order(self.pair, 'limit', 'buy', 1 / self.bid, price=self.bid)
        self.buy_ex['order id history'].append(order['id'])
        if wait:
            wait_for_fill(self.pair, self.buy_ex['client'], order['id'])
            new_tick = self.sell_ex['client'].fetch_ticker(self.pair)
            if new_tick['bid'] > self.ask:
                print('Note: price has gone up - ask increased')
                self.ask = new_tick['ask'] * 0.999
            elif new_tick['ask'] < self.ask:
                print('Warning: price has gone down drastically - ask decreased to panic sell')
                self.ask = new_tick['ask'] * 0.999

        if self.sep_fees:
            amount = 1 / self.bid - self.buy_ex['wfee']
        else:
            amount = (1 - self.buy_ex['tfee']) / self.bid - self.buy_ex['wfee']

        order = self.sell_ex['client'].create_order(self.pair, 'limit', 'sell', amount, price=self.ask)
        self.sell_ex['order id history'].append(order['id'])
        if wait:
            wait_for_fill(self.pair, self.buy_ex['client'], order['id'])


class BinanceKucoinArbBot:
    """ Simple bespoke arb bot. Start with balances in both exchanges a little more than the value of funds """
    def __init__(self, base, quote, binance_client, kucoin_client, funds=1):
        self.funds = funds  # amount (in quote curr) of each coin on both exchanges (e.g. total amount/4)
        self.base = base
        self.quote = quote
        self.pair = base + '/' + quote
        self.clients = {
            'Binance': {
                'client': binance_client,
                'wfee': (0.1, 0.1),  # manually enter fees for now (base, quote)
                'tfee': 0.001,
                'bals': [(binance_client.fetch_balance()[base]['total'], binance_client.fetch_balance()[quote]['total'])],
                'orders': []
            },
            'Kucoin': {
                'client': kucoin_client,
                'wfee': (0.1, 0.1),  # manually enter fees for now (base, quote)
                'tfee': 0.001,
                'bals': [
                    (kucoin_client.fetch_balance()[base]['total'], kucoin_client.fetch_balance()[quote]['total'])],
                'orders': []
            }
        }
        self.logs = {
            'base funds': [self.clients['Binance']['bals'][0][0] + self.clients['Kucoin']['bals'][0][0]],
            'quote funds': [self.clients['Binance']['bals'][0][1] + self.clients['Kucoin']['bals'][0][1]],
            '% inc base': [0],
            '% inc quote': [0],
            'ts': [datetime.utcnow()]
        }

        self.margin_threshold = 0.012  # minimum margin after fees
        self.check()

    def step(self):
        # check prices
        print('Checking prices...')
        check = self.check()
        if not check:
            print('Insufficient margin')
            return
        self._funds_check()

        # simultaneously trade
        print('Executing trades...')
        self.trade()

        # withdraw
        print('Withdrawing...')
        self.withdraw()
        print('Waiting for deposits...')
        self._wait_for_deposits()

        # update logs

    def check(self):
        df = compare_order_books(self.base, self.quote, (self.clients['Binance']['client'], self.clients['Kucoin']['client']))
        self.price = sum(df.iloc[0].values[1:-3]) / 4
        print(df)

        if df['% diff'][0] < 0:
            return False

        self.buy = df['buy'][0]
        self.sell = df['sell'][0]
        buy_price = calc_market_price(self.base, self.quote, self.funds, self.clients[self.buy]['client'])
        sell_price = calc_market_price(self.base, self.quote, self.funds, self.clients[self.sell]['client'])
        aprox_gain = (sell_price/buy_price - 1 - self.margin_threshold) * 100

        print('Aprox gain = {:.2f}%'.format(aprox_gain))
        if aprox_gain < 0:
            return False

    def trade(self):
        pass
        # quick buy

    def withdraw(self):
        pass

    def _funds_check(self):
        bals = []
        for c in self.clients:
            bals.append(self.clients[c]['bals'][-1][0] * self.price)
            bals.append(self.clients[c]['bals'][-1][1])
        if min(bals) < self.funds:
            self.funds = 0.9 * min(bals)
            print('Warning: funds too large for balances. Resized to {}'.format(self.funds))

    def _wait_for_deposits(self):
        # this is awful code
        bal = {}
        for c in self.clients:
            bal_idx = 1 if self.clients[c]['side'] == 'buy' else 0
            coin = self.base if bal_idx == 0 else self.quote
            bal[c] = self.clients[c]['client'].fetch_balance()[coin]['total']
        flags = 0
        while flags < 2:
            flags = 0
            for c in self.clients:
                bal_idx = 1 if self.clients[c]['side'] == 'buy' else 0
                coin = self.base if bal_idx == 0 else self.quote
                if bal[c] < self.clients[c]['client'].fetch_balance()[coin]['total']:
                    flags += 1
            time.sleep(120)

    def _update_logs(self):
        self.clients['Binance']['bals'].append((self.clients['Binance']['client'].fetch_balance()[self.base]['total'],
                                                self.clients['Binance']['client'].fetch_balance()[self.quote]['total']))
        self.clients['Kucoin']['bals'].append((self.clients['Kucoin']['client'].fetch_balance()[self.base]['total'],
                                                self.clients['Kucoin']['client'].fetch_balance()[self.quote]['total']))
        self.logs['base funds'].append(self.clients['Binance']['bals'][-1][0] + self.clients['Kucoin']['bals'][-1][0])
        self.logs['quote funds'].append(self.clients['Binance']['bals'][-1][1] + self.clients['Kucoin']['bals'][-1][1])
        self.logs['% inc base'].append((self.logs['base funds'][-1] / self.logs['base funds'][-2] - 1) * 100)
        self.logs['% inc quote'].append((self.logs['quote funds'][-1] / self.logs['quote funds'][-2] - 1) * 100)
        self.logs['ts'].append(datetime.utcnow())

def get_client_info(client, withdraw_coin):
    """ Parsing useful info into dict"""
    info = {
        'client': client,
        'name': client.describe()['name'],
        'order id history': []
    }
    try:
        info['tfee'] = client.describe()['fees']['trading']['taker']
    except KeyError:
        info['tfee'] = 0.003
        print('Warning: {} taker fee assumed to be 0.3%'.format(info['name']))
    try:
        info['wfee'] = client.describe()['fees']['funding']['withdraw'][withdraw_coin]
    except KeyError:
        info['wfee'] = 0
        print('Warning: {} withdrawal fee assumed to be 0'.format(info['name']))
    if info['wfee'] is None:
        info['wfee'] = 0
        print('Warning: {} withdrawal fee assumed to be 0'.format(info['name']))

    print(info)
    return info


if __name__ == '__main__':
    # print(single_arb_pair_check('LTC', 'BTC', 2, (CLIENTS['Binance'], CLIENTS['Kucoin'])))
    # bot = ArbPairBot('VEN', 'ETH', CLIENTS['Binance'], CLIENTS['Kucoin'], funds=100, market_orders=True, seperate_taker_fees=True)
    # bot = ArbPairBot('B', 'Q', TESTCLIENTS['C0'], TESTCLIENTS['C1'], funds=100)
    # bot = ArbPairBot('BCH', 'ETH', CLIENTS['Binance'], CLIENTS['Kucoin'], funds=100, market_orders=True,
    #                  seperate_taker_fees=True)
    # print(bot.check())

    bot = BinanceKucoinArbBot('MOD', 'ETH', CLIENTS['Binance'], CLIENTS['Kucoin'])