# %%
import os
import sys
from pathlib import Path
import json
import yaml
import ccxt
root = os.path.join('..')
sys.path.append(root)
import util

with open('../api_keys.yaml') as f:
    API_KEYS = yaml.load(f)

CLIENTS = {
    'BINANCE': ccxt.binance(API_KEYS['BINANCE']),
    # 'GDAX': ccxt.gdax(API_KEYS['GDAX'])
}

# %%
with open('../trades_to_make.json') as f:
    trades_to_make = json.load(f)

trades_completed = []
# %%

client = CLIENTS['BINANCE']
for i, t in enumerate(trades_to_make):
    if i not in trades_completed:
        print(t)
        try:
            order = util.quick_limit_order(
                client,
                t['symbol'],
                t['direction'],
                t['fcurr_amount'],
                amount_to_lots=True,
                execute=True)
            print(order)
            try:
                util.wait_for_fill(t['symbol'], client, order['id'], timeout=120)
            except TimeoutError as e:
                raise e  # Adjust order
        except Exception as e:
            print(e)
            pass

# %%

# ids = [order['id'] for order in client.fetch_open_orders('XRP/ETH')]
# for _id in ids:
    # r = client.cancel_order(_id, 'XRP/ETH')
    # print(r)
