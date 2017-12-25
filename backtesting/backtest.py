import os
import sys
from pathlib import Path
import sqlite3
import pandas as pd

cwd = os.path.dirname(os.path.realpath(__file__))
root = Path(cwd).parents[0]
sys.path.append(str(root))

from trade.bots import Bot
from rule_sets.rule_sets import rule_sets

with sqlite3.connect(os.path.join(cwd, 'exchange_data.db')) as con:
	cur = con.cursor()
	cur.execute('select * from exchange_data where exchange = "Coinbase" and pair = "BTCEUR"')
	records = cur.fetchall()

# print(len(records))
cols = [desc[0] for desc in cur.description]
df = pd.DataFrame(records, columns=cols)
df.drop('Unnamed: 0', axis=1, inplace=True)
df['ts'] = pd.DatetimeIndex(df['ts'])
df.sort_values(['ts'], inplace=True)
	

bot = Bot(100, rule_sets['nick_test_1'])
for price in df['price']:
	bot.step(price)


