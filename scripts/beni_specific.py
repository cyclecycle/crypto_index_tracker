from trade.util import get_total_balance
from private import CLIENTS  # Dict of ccxt clients instantiated with private API keys
import numpy as np


def profit():
    df = get_total_balance(CLIENTS, wallets={'SC': 11740}, gbp_only=False)
    print(df)
    funds_invested = 4500
    current_value = df['Total (GBP)'].values[-2]
    profit = current_value - funds_invested
    profitperc = 100 * profit/funds_invested
    print('Invested: £{:.2f}, Current Value: £{:.2f}, Profit: £{:.2f}, {:+.2f}%'.format(
            funds_invested, current_value, profit, profitperc))


if __name__ == '__main__':
    # np.set_printoptions(precision=2)
    profit()
