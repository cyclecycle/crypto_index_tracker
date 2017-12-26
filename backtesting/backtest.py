import os
import sys
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml

cwd = os.path.dirname(os.path.realpath(__file__))
root = Path(cwd).parents[0]
sys.path.append(str(root))

from trade.bots import Bot


''' Load historical data '''
with sqlite3.connect(os.path.join(cwd, 'exchange_data.db')) as con:
    cur = con.cursor()
    cur.execute('select * from exchange_data where exchange = "Coinbase" and pair = "BTCEUR"')
    records = cur.fetchall()
    # print(len(records))


''' Prepare dataframe '''
cols = [desc[0] for desc in cur.description]
df = pd.DataFrame(records, columns=cols)
df.drop('Unnamed: 0', axis=1, inplace=True)
df['ts'] = pd.DatetimeIndex(df['ts'])
df.sort_values(['ts'], inplace=True)

df = df[20:]  # Time gap between first samples. Bot will need to be able to handle this but for now it's easier to read the graph without it


''' Load rule set and instantiate bot '''
with open(os.path.join(root, 'rule_sets/rs1.yaml')) as f:
    rule_set = yaml.load(f)

start_funds = 100

bot = Bot(
    start_funds,
    rule_set,
    memory_size=len(records),
    verbose=True
)


''' Run simulation '''
for price in df['price']:
    bot.step(price)


''' Summary '''
actions = bot.memory['action']
buy_idx = [i for i, action in enumerate(actions) if action['action'] == 'buy']
sell_idx = [i for i, action in enumerate(actions) if action['action'] == 'sell']
print('start funds:', start_funds)
print('n buys:', len(buy_idx))
print('n sells:', len(sell_idx))
print('end funds', bot.funds)
# Actions log to csv
pd.DataFrame(actions).loc[buy_idx + sell_idx].sort_values(['timestamp']).to_csv(os.path.join(cwd, 'action_log.csv'), index=False)

''' Plot '''
y = np.array(bot.memory['price'])
x = np.arange(len(y))
f, (ax1, ax2) = plt.subplots(2, sharex=True)
ax1.scatter(x, y, s=0.2)
ax1.plot(bot.memory['sma10'], c='r')
ax1.plot(bot.memory['sma45'], c='c')
ax2.plot(bot.memory['sma10_gradient'], c='r')
ax2.plot(bot.memory['sma45_gradient'], c='c')
# Add buy and sell markers
# plt.show()
