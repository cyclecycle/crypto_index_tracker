from bots import CoreBot
from coinmarketcap import Market

class IndexTracker(CoreBot):
    ''' Each step, rebalance portfolio based on observables and weighting dict '''

    def get_coin_data(self, n_coins):
        coinmarketcap = Market()
        coin_data = coinmarketcap.ticker(limit=n_coins, convert='EUR')
        return coin_data

    def calc_weightings(self, coin_data_list, weighting_dict):
        symbols = [dd['symbol'] for dd in coin_data_list]
        ''' Get relevant values for calculating weights '''
        keys_of_interest = weighting_dict.keys()
        sym2vals = {sym: {} for sym in symbols}
        for dd in coin_data_list:
            symbol = dd['symbol']
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
        ''' Integrate proportions using weighting_dict '''
        sym2weights = {sym: {} for sym in symbols}
        for sym, props in sym2props.items():
            for key, coeff in weighting_dict.items():
                weight = props[key] * coeff
                sym2weights[sym] = round(weight, 3)
        # assert sum(sym2weights.values()) == 1, 'Weights do not sum to 1'
        return sym2weights

    def rebalance(self, coin_data_list, weighting_dict):
        coin_data_list = self.memory[coin_data_list][-1]
        sym2weights = self.calc_weightings(coin_data_list, weighting_dict)
        print(sym2weights)
        ''' Compare new weights to current positions, decide what buys and sells should be made, taking the best available route '''


if __name__ == '__main__':

    bot = IndexTracker(funds=1000)
    bot.load_rule_set('index_tracker.yaml')
    bot.step()
