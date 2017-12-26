from private import CLIENTS  # Dict of ccxt clients instantiated with private API keys
import ccxt

kraken = CLIENTS['Kraken']

# print([mar['symbol'] for mar in kraken.fetch_markets()])
#
# print(kraken.create_order('XMR/EUR', 'limit', 'sell', 0.1, price=400))

binance = CLIENTS['Binance']
print(binance.fetch_balance()['total'])