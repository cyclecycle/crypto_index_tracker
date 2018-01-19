import os
import sys
from pathlib import Path
from collections import OrderedDict
import sqlite3
import numpy as np
import pandas as pd
import yaml
cwd = os.path.dirname(os.path.realpath(__file__))
root = Path(cwd).parents[0]
sys.path.append(str(root))


exchange_data_db = os.path.join(cwd, 'data/exchange_data.db')


def get_exchanges_to_pairs():
    with sqlite3.connect(exchange_data_db) as con:
        cur = con.cursor()
        cur.execute('select distinct(pair), exchange from exchange_data')
        records = cur.fetchall()
    exchanges2pairs = {}
    for pair, exchange in records:
        try:
            exchanges2pairs[exchange].append(pair)
        except:
            exchanges2pairs[exchange] = [pair]
    return exchanges2pairs


def get_dataset(pair, exchange):
    with sqlite3.connect(exchange_data_db) as con:
        cur = con.cursor()
        cur.execute('select * from exchange_data where pair = ? and exchange = ?', (pair, exchange))
        records = cur.fetchall()
        columns = [c[0] for c in cur.description]
    df = pd.DataFrame(records, columns=columns)
    df.drop(['Unnamed: 0'], axis=1, inplace=True)
    df.sort_values(['ts'], inplace=True)
    return df


if __name__ == '__main__':
    exchanges2pairs = get_exchanges_to_pairs()
    df = get_dataset('IOTBTC', 'Binance')
    print(df)
