from trade.util import get_total_balance
from private import CLIENTS  # Dict of ccxt clients instantiated with private API keys


if __name__ == '__main__':
    df = get_total_balance(CLIENTS, wallets={'SC': 11740, 'XRB': 47.7}, gbp_only=False, funds_invested=5500)
