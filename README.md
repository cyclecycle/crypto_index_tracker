# Crypto trading tools #
Tools for trading crypto on multiple exchanges. Planning to use for:
- arbitrage
- minute level trading strategies on single currency pairs
- using one exchange to predict near future performance of another

Additional module info in each module's README.

### TODO ###
(incomplete)
- test reliability of prices and trading clients for each exchange of interest
- build exchange whitelist with info for each exchange
- search currency pairs for good arb oppurtunities
- develop abstract bot class?

### Repo Structure ###
2 main modules:
- the trade module deals with exchange clients. Includes bot classes and tools for accessing accounts on exchanges.
- the prices module deals with price fetching functions

### Dependencies ###
pip install:
ccxt
cryptocompy
pandas
numpy
forex python
