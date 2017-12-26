import ccxt
from forex_python.converter import CurrencyRates
import pandas as pd
from cryptocompy import price

FIAT = ['GBP', 'USD', 'EUR']


def get_total_balance(clients, gbp_only=False, wallets=None, funds_invested=None):
    """
    Analyses balance of funds across one or more exchanges.
    :param clients: Dict of ccxt authenticated clients with exchange names as keys
    :param wallets: optional dict of coins held in private wallets (e.g. {'BTC': 1.1, 'LTC': 0.02})
    :param gbp_only: optionally return GBP values only
    :param funds_invested: optionally input GBP invested for profit calculation
    :return: DataFrame of balance
    """
    eur2gbp = CurrencyRates().get_rate('EUR', 'GBP')
    pd.set_option('expand_frame_repr', False)
    pd.options.display.float_format = '{:.2f}'.format


    # build df columns from currencies
    df_cols = ['Exchange']
    totals = {}
    coins = set()
    for ex in clients:
        totals_raw = clients[ex].fetch_balance()['total']
        totals[ex] = {}
        for curr in totals_raw:
            if totals_raw[curr] > 0.:
                totals[ex][curr] = totals_raw[curr]
        for curr in totals[ex]:
            if curr not in FIAT:
                coins.add(curr)
    # add wallets
    totals['Wallets'] = {}
    for curr in wallets:
        totals['Wallets'][curr] = wallets[curr]
        coins.add(curr)

    df_cols += list(coins) + ['EUR', 'GBP', 'Total (GBP)']
    df = pd.DataFrame(columns=df_cols)
    avg_prices = price.get_current_price(list(coins), 'EUR')

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
            elif col == 'GBP' or col == 'Total (GBP)':
                row_gbp_totals[col] = row_totals[col]
            else:
                row_gbp_totals[col] = row_totals[col] * avg_prices[col]['EUR'] * eur2gbp
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
            perc_row[col] = '%'
        else:
            perc_row[col] = 100 * df[col].values[-1] / df['Total (GBP)'].values[-1]
    perc_row['%'] = 100
    df = df.append(perc_row, ignore_index=True)

    # formatting and sorting
    df = df.loc[:, (df > 1).any(axis=0)]  # delete columns with less than £1 in
    df = df[:-3].sort_values(by='%', ascending=False).reset_index(drop=True).append(df[-3:], ignore_index=True)
    df = pd.concat(
        [df.iloc[:, 0], df.iloc[:, 1:-3].sort_values(by=len(df) - 1, ascending=False, axis=1), df.iloc[:, -3:]], axis=1)

    print(df)

    # profit calc
    if funds_invested is not None:
        current_value = df['Total (GBP)'].values[-2]
        profit = current_value - funds_invested
        profitperc = 100 * profit/funds_invested
        print('\nInvested: £{:.2f}, Current Value: £{:.2f}, Profit: £{:.2f}, {:+.2f}%'.format(
                funds_invested, current_value, profit, profitperc))

    if gbp_only:
        return df[['Exchange', 'Total (GBP)']][:-2]
    else:
        return df


if __name__ == '__main__':
    pass