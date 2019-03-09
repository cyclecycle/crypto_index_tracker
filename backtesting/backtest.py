import os
import sys
from pathlib import Path
from collections import OrderedDict
from itertools import product
import copy
from pprint import pprint
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml
cwd = os.path.dirname(os.path.realpath(__file__))
root = Path(cwd).parents[0]
sys.path.append(str(root))
# from trade.core_bot import Bot
# from trade.bot_indicators import Indicators
# from trade.bot_optimise import BotOptimiser
import helpers
from backtesting import util

start_funds = 100


def flatten(l):
    return [sublist for _list in l for sublist in _list]


def backtest(bot, dataset, plot=False):

    ''' Run simulation '''
    for idx, row in dataset.iterrows():
        bot.step(**dict(row))

    ''' Results '''
    actions = pd.DataFrame(bot.memory['action'])
    buys = actions.loc[actions['action'] == 'buy']
    sells = actions.loc[actions['action'] == 'sell']
    results = OrderedDict({
        'start funds': start_funds,
        'n samples': len(dataset),
        'start price': dataset.loc[0, 'price'],
        'end price': dataset.loc[len(dataset)-1, 'price'],
        'n buys': len(buys),
        'n sells': len(sells),
        'end funds': bot.funds,
        'net': bot.funds - start_funds
    })

    # Actions log to csv
    # actions.loc[actions['action'].isin(['buy', 'sell'])].sort_values(['timestamp']).to_csv(os.path.join(cwd, 'action_log.csv'), index=False)

    if plot:

        y = np.array(bot.memory['price'])
        x = np.arange(len(y))
        f, (ax1, ax2) = plt.subplots(2, sharex=True)
        # f, (ax1) = plt.subplots(1)
        ax1.scatter(x, y, s=0.5)
        ax1.plot(bot.memory['sma_1'], c='r')
        ax1.plot(bot.memory['sma_2'], c='c')
        if not buys.empty and not sells.empty:
            ax1.scatter(buys.index, buys['price'], c='g', marker='x')
            ax1.scatter(sells.index, sells['price'], c='y', marker='x')

        ax1.set_ylim([sorted(y)[0], sorted(y)[-1]])

        # ax2.plot(bot.memory['sma_1_gradient'], c='r')
        # ax2.plot(bot.memory['sma_2_gradient'], c='c')

        # ax3.plot(bot.memory['funds'])

        plt.show()

    return results


def optimise_bot(bot, dataset, optimise_vars):
    ''' For each combination of optimise_vars, create and load a new rule set, run simulation and record results '''
    ''' Implement in BotOptimiser '''
    ''' Grid search '''
    results = []
    best_rule_set = None
    best_net = 0
    print(len(list(product(*optimise_vars.values()))))
    raise
    for i, comb in enumerate(product(*optimise_vars.values())):
        print(i)
        test_vars = dict(zip(optimise_vars.keys(), comb))
        new_rule_set = bot.raw_rule_set.copy()
        del new_rule_set['vars']
        test_bot = copy.copy(bot)
        test_bot.rule_set = helpers.recursive_replace(new_rule_set, test_vars)
        result = backtest(test_bot, dataset)
        results.append(result)
        if result['net'] > best_net:
            best_rule_set = new_rule_set
            best_net = result['net']
        # pprint(result)
        # print('best_rule_set:', best_rule_set)
        # print('best_net:', best_net)
    return results, best_rule_set, best_net

    # print(bot.rule_set)

if __name__ == '__main__':

    # results_list = []
    df = util.get_dataset('BTCEUR', 'Bitfinex')
    df = df.iloc[-2:]
    df.reset_index(inplace=True)
    # exchange = df.loc[0, 'exchange']
    # pair = df.loc[0, 'pair']
    # results = backtest(df, plot=True)
    # results.update({'exchange': exchange, 'pair': pair})
    # results_list.append(results)
    #
    # pd.DataFrame(results_list).sort_values(['end funds']).to_csv(os.path.join(cwd, 'results.csv'), index=False)

    from trade.wilson_bot import Wilson

    optimise_vars = {
        '$sma_1_len': list(range(5, 300, 10)),
        '$sma_2_len': list(range(20, 500, 10)),
        '$sma_1_gradient_len': list(range(5, 300, 10)),
        '$sma_2_gradient_len': list(range(20, 500, 10)),
        '$sma_1_buy_gradient': list(range(0, 90, 10)),
        '$sma_2_buy_gradient': list(range(0, 90, 10)),
        '$sma_1_sell_gradient': list(range(0, -90, -10)),
        '$sma_2_sell_gradient': list(range(0, -90, -10)),
    }

    dataset = df

    bot = Wilson()
    bot.load_rule_set(os.path.join(root, 'trade/rule_sets/rs2.yaml'))
    results, best_rule_set, best_net = optimise_bot(bot, dataset, optimise_vars)
    print(best_rule_set, best_net)
