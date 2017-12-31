import os
import sys
from pathlib import Path
from collections import OrderedDict
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml
cwd = os.path.dirname(os.path.realpath(__file__))
root = Path(cwd).parents[0]
sys.path.append(str(root))
from trade.bots import Bot


start_funds = 100


def flatten(l):
    return [sublist for _list in l for sublist in _list]


def get_datasets():
    with sqlite3.connect(os.path.join(cwd, 'exchange_data.db')) as con:
        cur = con.cursor()
        cur.execute('select distinct(exchange) from exchange_data')
        exchanges = flatten(cur.fetchall())
        print(exchanges)
        cur.execute('select distinct(pair) from exchange_data')
        pairs = flatten(cur.fetchall())
        print(pairs)
        raise
        for exchange in exchanges:
            for pair in pairs:

                ''' Load historical data '''
                cur.execute('select * from exchange_data where exchange = ? and pair = ?', (exchange, pair))
                records = cur.fetchall()
                try:
                    if records[0][0]:

                        ''' Prepare dataframe '''
                        cols = [desc[0] for desc in cur.description]
                        df = pd.DataFrame(records, columns=cols)
                        df.drop('Unnamed: 0', axis=1, inplace=True)
                        df['ts'] = pd.DatetimeIndex(df['ts'])
                        df.sort_values(['ts'], inplace=True)

                        df = df[20:]  # Temporary
                        df.reset_index(inplace=True)

                        yield df
                except:
                    pass


def backtest(df, plot=False):

    ''' Instantiate bot '''
    bot = Bot(
        funds=start_funds,
        memory_size=len(df),
        # verbose=True
    )

    bot.load_rule_set('rs2.yaml')


    ''' Run simulation '''
    for price in df['price']:
        data = {'price': price}
        bot.step(**data)


    ''' Results '''
    actions = pd.DataFrame(bot.memory['action'])
    buys = actions.loc[actions['action'] == 'buy']
    sells = actions.loc[actions['action'] == 'sell']
    results = OrderedDict({
        'start funds': start_funds,
        'n samples': len(df),
        'start price': df.loc[0, 'price'],
        'end price': df.loc[len(df)-1, 'price'],
        'n buys': len(buys),
        'n sells': len(sells),
        'end funds': bot.funds,
        'net': bot.funds - start_funds
    })

    print(results)

    # Actions log to csv
    # actions.loc[actions['action'].isin(['buy', 'sell'])].sort_values(['timestamp']).to_csv(os.path.join(cwd, 'action_log.csv'), index=False)

    if not buys.empty and not sells.empty:
        if plot:

            y = np.array(bot.memory['price'])
            x = np.arange(len(y))
            # f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
            f, (ax1) = plt.subplots(1)
            ax1.scatter(x, y, s=0.5)
            ax1.plot(bot.memory['sma_1'], c='r')
            ax1.plot(bot.memory['sma_2'], c='c')
            ax1.scatter(buys.index, buys['price'], c='g', marker='x')
            ax1.scatter(sells.index, sells['price'], c='y', marker='x')

            # ax2.plot(bot.memory['sma10_gradient'], c='r')
            # ax2.plot(bot.memory['sma45_gradient'], c='c')

            # ax3.plot(bot.memory['funds'])

            plt.show()
            raise

    return results


if __name__ == '__main__':

    results_list = []
    for df in get_datasets():
        exchange = df.loc[0, 'exchange']
        pair = df.loc[0, 'pair']
        results = backtest(df, plot=True)
        results.update({'exchange': exchange, 'pair': pair})
        results_list.append(results)

    pd.DataFrame(results_list).sort_values(['end funds']).to_csv(os.path.join(cwd, 'results.csv'), index=False)

