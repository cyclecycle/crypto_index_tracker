import os
from pathlib import Path
import pickle
import ccxt
# from forex_python.converter import CurrencyRates
import pandas as pd
from cryptocompy import price
import yaml

FIAT = ['GBP', 'USD', 'EUR']

CWD = os.path.dirname(os.path.realpath(__file__))
ROOT = Path(CWD).parents[0]
with open(os.path.join(ROOT, 'trade/api_keys.yaml')) as f:
    API_KEYS = yaml.load(f)

CLIENTS = {
    'BINANCE': ccxt.binance(API_KEYS['BINANCE']),
    # 'GDAX': ccxt.gdax(API_KEYS['GDAX'])
}


def get_total_balance(clients, gbp_only=False):
    """Returns df of total balance over all exchanges"""
    eur2gbp = CurrencyRates().get_rate('EUR', 'GBP')

    # build df columns from currencies
    df_cols = ['Exchange']
    totals = {}
    coins = set()
    for ex in clients:
        totals[ex] = clients[ex].fetch_balance()['total']
        for curr in totals[ex]:
            if curr not in FIAT:
                coins.add(curr)
    df_cols += list(coins) + ['EUR', 'GBP', 'Total (GBP)']
    df = pd.DataFrame(columns=df_cols)
    avg_prices = price.get_current_price(list(coins), 'EUR')
    print(df_cols)

    # build row values for each exchange
    for ex in totals:
        row = {}
        total_gbp = 0
        for col in df:
            if col == 'Exchange':
                row['Exchange'] = ex
            elif col in totals[ex]:
                row[col] = totals[ex][col]
                if col == 'EUR':
                    total_gbp += row[col] * eur2gbp
                elif col == 'GBP':
                    total_gbp += row[col]
                else:
                    total_gbp += row[col] * avg_prices[col]['EUR'] * eur2gbp
            else:
                row[col] = 0.
        row['Total (GBP)'] = total_gbp
        df = df.append(row, ignore_index=True)

    # total all exchanges in each curr and GBP
    row_totals = {}
    row_gbp_totals = {}
    for col in df_cols:
        if col == 'Exchange':
            row_totals['Exchange'] = 'Total'
            row_gbp_totals['Exchange'] = 'Total (GBP)'
        else:
            row_totals[col] = sum(df[col].values)
            if col == 'EUR':
                row_gbp_totals[col] = row_totals[col] * eur2gbp
                print(eur2gbp)
            elif col == 'GBP' or col == 'Total (GBP)':
                row_gbp_totals[col] = row_totals[col]
            else:
                row_gbp_totals[col] = row_totals[col] * avg_prices[col]['EUR'] * eur2gbp
    print(row_gbp_totals)
    df = df.append(row_totals, ignore_index=True)
    df = df.append(row_gbp_totals, ignore_index=True)

    # add percentage of funds stored in each exchange
    perc_col = []
    for i, row in df.iterrows():
        if row['Exchange'] != 'Total':
            perc_col.append(100 * row['Total (GBP)'] / df['Total (GBP)'].values[-1])
    perc_col.append(100)
    df['%'] = perc_col

    # add percentage of funds in each curr
    perc_row = {}
    for col in df_cols:
        if col == 'Exchange':
            perc_row[col] = 'Total %'
        else:
            perc_row[col] = 100 * df[col].values[-1] / df['Total (GBP)'].values[-1]
    perc_row['%'] = 100
    df = df.append(perc_row, ignore_index=True)

    df = df.loc[:, (df != 0).any(axis=0)]  # delete columns where everything is 0

    if gbp_only:
        return df[['Exchange', 'Total (GBP)']][:-2]
    else:
        return df


def get_pair_data_list(client, use_checkpoint=False):
    checkpoint_path = os.path.join(CWD, 'checkpoints/pair_data_list_checkpoint.p')
    if use_checkpoint:
        with open(checkpoint_path, 'rb') as f:
            return pickle.load(f)
    markets = client.load_markets()
    pair_data_list = []
    for symbol, dd in markets.items():
        ticker = client.fetch_ticker(symbol)
        pair_data_list.append({
            'fsym': dd['base'],
            'tsym': dd['quote'],
            'price': ticker['last'],
            'symbol': symbol,
            'direction': 'buy',
            'exchange': client.name
        })
    pair_data_list = get_inv_pairs(pair_data_list)
    with open(checkpoint_path, 'wb') as f:
        pickle.dump(pair_data_list, f)
    return pair_data_list


def symbols_in_pair_data_list(pair_data_list):
    return list(set([sublist for _list in [[d['tsym'], d['fsym']] for d in pair_data_list] for sublist in _list]))


def get_inv_pairs(pair_data_list):
    pairs_inv = []
    for pair in pair_data_list:
        pair_inv = pair.copy()
        try:
            pair_inv['price'] = 1 / pair['price']
            pair_inv['fsym'] = pair['tsym']
            pair_inv['tsym'] = pair['fsym']
            pair_inv['direction'] = 'sell'
            pairs_inv.append(pair_inv)
        except ZeroDivisionError as e:
            pass
    pair_data_list = pair_data_list + pairs_inv
    return pair_data_list


if __name__ == '__main__':
    print(get_total_balance(CLIENTS, gbp_only=False))



