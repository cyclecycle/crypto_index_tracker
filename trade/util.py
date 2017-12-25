from private import CLIENTS  # Dict of ccxt clients instantiated with private API keys
import ccxt
from forex_python.converter import CurrencyRates
import pandas as pd
from cryptocompy import price

FIAT = ['GBP', 'USD', 'EUR']


def get_total_balance(clients, gbp_only=False):
    """
    Analyses balance of funds across one or more exchanges.
    :param clients: Dict of ccxt authenticated clients with exchange names as keys
    :param gbp_only: optionally return GBP values only
    :return: DataFrame of balance
    """
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


if __name__ == '__main__':
    print(get_total_balance(CLIENTS, gbp_only=False))