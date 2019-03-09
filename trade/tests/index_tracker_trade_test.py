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

print(trades_to_make)
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
                trades_completed.append(i)
            except TimeoutError as e:
                raise e  # Adjust order
        except Exception as e:
            print(e)
            pass

# %%

print(trades_completed)

# %%

# ids = [order['id'] for order in client.fetch_open_orders('VEN/ETH')]
# for _id in ids:
#     r = client.cancel_order(_id, 'VEN/ETH')
#     print(r)
