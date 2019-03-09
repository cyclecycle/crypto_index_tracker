"""
Visualise, annotate, and draw stats from tracked exchange data
"""

# %%

import os
import sys
from pathlib import Path
from pprint import pprint
import sqlite3
from collections import OrderedDict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml
cwd = os.path.dirname(os.path.realpath('__file__'))
root = Path(cwd).parents[0]
sys.path.append(str(root))
import helpers
from backtesting import util
%matplotlib inline

# %%  Get data

df = util.get_dataset('BTCEUR', 'Bitfinex')

# %%  Time range

start = df.sort_values(['ts']).iloc[0]['ts']
end = df.sort_values(['ts']).iloc[-1]['ts']
time_range = end - start
print(time_range)

# %% For each row get the time since last the last row

time_since_last = [ts - df.iloc[i-1]['ts'] for i, ts in enumerate(df.iloc[1:]['ts'], start=1)]
time_since_last = [np.nan] + time_since_last  # Not applicable for first value
assert len(time_since_last) == len(df)
df['time_since_last_ts'] = time_since_last
print(df['time_since_last_ts'])

# %%  Plot time_since_last_ts

df.plot(y='time_since_last_ts')

# %%  Label epochs of continuous data

epoch_cutoff_time_minutes = 5

first_epoch = 0
epoch2idx = {first_epoch: [list(df.index)[0]]}  # First idx will be in the first epoch
current_epoch = first_epoch
for idx, row in df.iloc[1:].iterrows():
    minutes_since_last = row['time_since_last_ts'].total_seconds() / 60
    if minutes_since_last <= epoch_cutoff_time_minutes:
        epoch2idx[current_epoch].append(idx)
    else:  # New epoch
        current_epoch += 1
        epoch2idx[current_epoch] = [idx]

# Add labels to df
for epoch, idx_list in epoch2idx.items():
    df.loc[idx_list, 'epoch'] = epoch

# %%  Arange epochs by length and visualise

epoch2idx = OrderedDict(sorted(epoch2idx.items(), key=lambda x: len(x[1]), reverse=True))
epoch2length = {epoch: len(idx_list) for epoch, idx_list in epoch2idx.items()}

pd.value_counts(df['epoch']).plot(kind='bar')

epoch_time_range = lambda epoch: df.loc[epoch2idx[epoch]].sort_values(['ts'])

# %%  Visualise
