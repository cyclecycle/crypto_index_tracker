from trade.util import wait_for_fill

pair = 'LTC/BTC'
base = 'LTC'
FUNDS = 1

def full_test(client):
    """
    Check basic trading functionality. Requires 1 LTC in exchange.
    Should:
    1) limit sell
    2) limit buy
    3) market sell
    4) market buy
    5) withdraw out

    Things to log:
    - fee given by ccxt
    - actual fee from order dict
    - change in balance
    - price of test


    """

    # Info

    # Limit orders
    ask = client.fetch_ticket(pair)['bid'] * 1.001
    order = client.create_order(pair, 'limit', 'sell', FUNDS, price=ask)
    wait_for_fill(pair, client, order['id'])

    amount = client.fetch_balance()['BTC']

    bid = client.fetch_ticket(pair)['ask'] * 0.999
    order = client.create_order(pair, 'limit', 'buy', FUNDS / bid, price=bid)
    wait_for_fill(pair, client, order['id'])




    # Market orders


    # Withdrawal

def market_order_test(client):
    #not sure if right

    print('Begin test')
    orig_bal = client.fetch_balance()
    print('Balance:   {} BTC,   {} LTC'.format(orig_bal['BTC']['total'], orig_bal['LTC']['total']))

    print('Market sell')
    order = client.create_order(pair, 'market', 'sell', FUNDS)
    order = wait_for_fill(pair, client, order['id'])

    print('Order details {}'.format(order))
    bal1 = client.fetch_balance()
    print('Balance:   {} BTC,   {} LTC'.format(bal1['BTC']['total'], bal1['LTC']['total']))

    # is there an amount in the order dict?
    # does it match the balance change?
    # print this

    amount = None
    order = client.create_order(pair, 'limit', 'buy', amount)
    order = wait_for_fill(pair, client, order['id'])


if __name__ == '__main__':
    pass