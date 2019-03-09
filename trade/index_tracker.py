from pprint import pprint
import os
import sys
from pathlib import Path
import pickle
import json
from pprint import pformat
from collections import OrderedDict
import numpy as np
from coinmarketcap import Market
from cryptocompy import price
import ccxt
import yaml
from core_bot import CoreBot
import util
import helpers

root = Path(os.path.dirname(os.path.realpath(__file__))).parents[0]
sys.path.append(str(root))

with open(os.path.join(root, 'trade/api_keys.yaml')) as f:
    API_KEYS = yaml.load(f)

with open(os.path.join(root, 'trade/coin_thesaurus.yaml')) as f:
    coin_thesaurus = yaml.load(f)

CLIENTS = {
    # 'GDAX': ccxt.gdax(API_KEYS['GDAX']),
    'BINANCE': ccxt.binance(API_KEYS['BINANCE'])
}


class IndexTracker(CoreBot):
    ''' Each step, rebalance portfolio based on weighting dict '''

    def rebalance(self, coin_data_list, metric_weights, coin_weight_coeffs, n_coins):
        self.client = ccxt.binance(API_KEYS['BINANCE'])
        self.log('Getting pair data list...')
        pair_data_list = util.get_pair_data_list(self.client, use_checkpoint=True)
        exchange_syms = util.symbols_in_pair_data_list(pair_data_list)
        self.log('Getting coin market cap data...')
        coin_data_list = self.memory[coin_data_list][-1]
        coin_data_list = helpers.recursive_replace(coin_data_list, coin_thesaurus)  # Standardise symbol names
        coin_data_list = [el for el in coin_data_list.values() if el['symbol'] in exchange_syms]

        # self.log('calculating desired spread...')
        # sym2weights = self.apply_metric_weights(coin_data_list, metric_weights)
        # sym2weights = self.apply_coin_coeffs(sym2weights, coin_weight_coeffs)
        # sym2weights = OrderedDict(sorted(sym2weights.items(), key=lambda x: x[1], reverse=True))
        # keep_syms = list(sym2weights)[:n_coins]
        # sym2weights = {sym: sym2weights[sym] for sym in keep_syms}
        # sym2weights = self.scale_weights_to_sum_1(sym2weights)
        # desired_spread = {sym: round(sym2weights[sym], 3) for sym in sym2weights}

        self.log('getting current positions...')
        positions = self.get_current_positions()
        pprint(positions)
        # positions.update({sym: 0 for sym in list(set(desired_spread.keys()) - set(positions.keys()))})  # Add null vals for coins not owned
        positions_eur = self.positions_to_values(positions)
        current_spread = self.positions_to_spread(positions_eur)
        current_sum_eur = sum(positions_eur.values())
        # desired_val_eur = self.spread_to_values(desired_spread, current_sum_eur)

        self.log('current positions (coin amounts)', positions)
        self.log('current positions (in EUR)', positions_eur)
        self.log('current total value (in EUR):', current_sum_eur)
        self.log('current spread:', current_spread)
        # self.log('desired positions (in EUR):', desired_val_eur)
        # self.log('desired spread:', self.sort_dict_desc(desired_spread))

        # trades_to_make = self.trades_to_make(positions, positions_eur, desired_val_eur, current_spread, desired_spread, pair_data_list)
        # self.log('trades to make', trades_to_make)
        # self.log(str(len(trades_to_make)) + ' trades')

        # with open(os.path.join(root, 'trade/trades_to_make.json'), 'w') as f:
        #     json.dump(trades_to_make, f, indent=2)

        # raise
        # results = self.execute_trades(trades_to_make)

    def trades_to_make(self, positions, positions_eur, desired_val_eur, current_spread, desired_spread, pair_data_list,
        fee_coeff=1-0.03, amounts_to_lots=False, min_trade_eur=1):

        trades_to_make = []

        ''' Which coins to buy or sell '''
        scale_factors = self.scale_old_spread_to_new(current_spread, desired_spread)
        coins_to_reduce = [sym for sym, factor in scale_factors.items() if factor < 1]
        coins_to_abolish = list(set(positions.keys()) - set(desired_spread.keys()))
        coins_to_increase = list(set(desired_spread) - set(coins_to_reduce))
        self.log('coins to reduce:', coins_to_reduce)
        self.log('coins to abolish:', coins_to_abolish)
        self.log('coins to buy:', coins_to_increase)

        ''' Excess to reallocate '''
        excess = {}
        for sym in coins_to_abolish:
            sell_amount = positions[sym]  # All
            excess[sym] = sell_amount
        for sym in coins_to_reduce:
            current_amount = positions[sym]
            reduction_factor = scale_factors[sym]
            keep_amount = current_amount * reduction_factor
            sell_amount = current_amount - keep_amount
            excess[sym] = sell_amount
        excess = self.sort_dict_desc(excess)
        excess_eur = self.sort_dict_desc({coin: self.coin_to_eur(coin, amount) for coin, amount in excess.items()})
        self.log('to relinquish (in coins):', excess)
        self.log('to relinquish (in EUR):', excess_eur)

        ''' Values to buy '''
        vals_to_buy = {coin: desired_val_eur[coin] - positions_eur[coin] for coin in desired_val_eur}
        vals_to_buy = {coin: val for coin, val in vals_to_buy.items() if val > min_trade_eur}
        vals_to_buy = self.sort_dict_desc(vals_to_buy)
        coin_to_buy = {coin: self.eur_to_coin(val, coin) for coin, val in vals_to_buy.items()}
        self.log('to buy (coin amounts)', coin_to_buy)
        self.log('to buy (in EUR)', vals_to_buy)

        ''' Reallocate excess '''
        self.log('calculating trades to make...')
        for tcurr, val_to_buy in vals_to_buy.items():
            excess_eur = self.sort_dict_desc(excess_eur)  # Trade most abundant coins first. Refresh for each tcurr.
            self.log('funds to reallocate (EUR)', excess_eur)
            for fcurr, funds_eur in excess_eur.items():
                """
                For each fcurr for which we have excess to reallocate, check if we still have more tcurr to buy,
                if so, trade fcurr for tcurr via the shortest route until val_to_buy is below 1 euro.
                """
                if val_to_buy > min_trade_eur and funds_eur > min_trade_eur:
                    self.log('buy ' + str(val_to_buy) + ' EUR worth of ' + tcurr + ' with ' + fcurr)
                    if funds_eur >= val_to_buy:
                        spend_eur = val_to_buy  # Put in much as needed
                    else:
                        spend_eur = funds_eur  # Put all in

                    route = util.shortest_path(util.find_trade_paths(fcurr, tcurr, pair_data_list))
                    if not route:
                        self.log('No route from ' + fcurr + ' to ' + tcurr)
                        continue

                    spend_amount = self.eur_to_coin(spend_eur, fcurr)
                    trade_outcomes = util.trade_path_outcomes(route, in_amount=spend_amount, fee_perc=0.005)

                    in_amount = spend_amount
                    for r, tcurr_amount in zip(route, trade_outcomes):
                        in_amount
                        trade = {
                            'symbol': r['symbol'],
                            'direction': r['direction'],
                            'fcurr': r['tsym'],
                            'tcurr': r['fsym'],
                            'fcurr_amount': in_amount,
                            'tcurr_amount': tcurr_amount
                        }
                        print(trade)
                        trades_to_make.append(trade)
                        in_amount = tcurr_amount  # Last out_amount is the next in_amount

                    ''' Update values after each trade '''
                    excess[fcurr] -= spend_amount
                    excess_eur[fcurr] -= spend_eur
                    val_to_buy -= spend_eur
        return trades_to_make

    def execute_trades(self, trades_to_make):
        results = []
        return results

    def apply_metric_weights(self, coin_data_list, metric_weights):
        symbols = [dd['symbol'] for dd in coin_data_list]
        ''' Get relevant values from coin_data_list '''
        keys_of_interest = metric_weights.keys()
        sym2vals = {sym: {} for sym in symbols}
        for dd in coin_data_list:
            symbol = dd['symbol']
            pprint(dd)
            raise
            for key in keys_of_interest:
                val = float(dd[key])
                sym2vals[symbol][key] = val
        ''' Values as proportions of totals '''
        totals = {key: sum([float(dd[key]) for dd in coin_data_list]) for key in keys_of_interest}
        sym2props = {sym: {} for sym in symbols}
        for sym, vals in sym2vals.items():
            for key in keys_of_interest:
                prop = vals[key] / totals[key]
                sym2props[sym][key] = prop
        ''' Integrate proportions using metric_weights '''
        sym2weights = {sym: {} for sym in symbols}
        for sym, props in sym2props.items():
            for key, coeff in metric_weights.items():
                weight = props[key] * coeff
                sym2weights[sym] = weight
        assert round(sum(sym2weights.values())) == 1, 'Weights do not sum to 1'
        return sym2weights

    def apply_coin_coeffs(self, sym2weights, coin_weight_coeffs):
        for coin, coeff in coin_weight_coeffs.items():
            try:
                new_weight = sym2weights[coin] * coeff
                sym2weights[coin] = new_weight
            except KeyError as e:  # Coin not in exchange so not in sym2weights
                pass
        return sym2weights

    ''' Data retrieval'''

    def get_coin_data(self):
        coinmarketcap = Market()
        coin_data = coinmarketcap.ticker(limit=300, convert='EUR')
        coin_data = coin_data['data']
        coin2eur = {d['symbol']: d['quotes']['EUR']['price'] for d in coin_data.values()}
        coin2eur = helpers.recursive_replace(coin2eur, coin_thesaurus)
        self.coin2eur = self.sort_dict_desc(coin2eur)
        return coin_data

    def get_current_positions(self):
        positions = self.client.fetch_balance()['total']
        positions = {sym: amount for sym, amount in positions.items() if amount > 0}
        positions = helpers.recursive_replace(positions, coin_thesaurus)
        positions = self.sort_dict_desc(positions)
        self.positions.append(positions)
        return positions

    ''' Convenience functions '''

    def positions_to_values(self, positions):
        values = {sym: self.coin_to_eur(sym, amount) for sym, amount in positions.items()}
        values = self.sort_dict_desc(values)
        return values

    def positions_to_spread(self, current_values):
        _sum = sum(current_values.values())
        spread = {sym: amount / _sum for sym, amount in current_values.items()}
        spread = self.sort_dict_desc(spread)
        return spread

    def spread_to_values(self, spread, current_eur_tot):
        values = {sym: current_eur_tot * prop for sym, prop in spread.items()}
        values = self.sort_dict_desc(values)
        return values

    def scale_old_spread_to_new(self, current_spread, desired_spread):
        ''' Find changes to make to current positions '''
        scale_factors = {}
        for sym, weight in desired_spread.items():
            try:
                current_prop = current_spread[sym]
                factor = weight / current_prop
                scale_factors[sym] = factor
            except ZeroDivisionError as e:  # Current position is zero
                scale_factors[sym] = np.nan
        scale_factors = self.sort_dict_desc(scale_factors)
        return scale_factors

    def scale_weights_to_sum_1(self, sym2weights):
        weights = sym2weights.values()
        _sum = sum(weights)
        factor = 1 / _sum
        sym2weights = {sym: sym2weights[sym] * factor for sym in sym2weights}
        assert round(sum(sym2weights.values())) == 1, 'Weights do not sum to 1'
        return sym2weights

    def coin_to_eur(self, coin, amount):
        price_eur = self.coin2eur[coin]
        return float(amount) * float(price_eur)

    def eur_to_coin(self, eur_amount, coin):
        price_eur = self.coin2eur[coin]
        return float(eur_amount) / float(price_eur)

    def sort_dict_desc(self, _dict):
        return OrderedDict(sorted(_dict.items(), key=lambda x: x[1], reverse=True))

    def query_yes_or_no(self, question):
        ''' Check user confirmation for testing purposes '''
        print(question)
        choice = input()
        if choice == 'y':
            return True
        return False


if __name__ == '__main__':

    bot = IndexTracker()
    bot.load_rule_set('index_tracker.yaml')
    bot.step()
