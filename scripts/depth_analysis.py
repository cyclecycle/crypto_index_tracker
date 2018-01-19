import matplotlib.pyplot as plt
import pandas as pd
import ast
from prices.trackers import DepthTracker
import ccxt


def plotdepth(ob, show=True):
    """ Plot cumulative depth chart from order book """
    x, y = [ob['bids'][0][0]], [ob['bids'][0][1]]
    for b in ob['bids'][1:]:
        x.append(b[0])
        y.append(b[1] + y[-1])
    plt.plot(x, y, color='g', label= 'bids')

    x, y = [ob['asks'][0][0]], [ob['asks'][0][1]]
    for a in ob['asks']:
        x.append(a[0])
        y.append(a[1] + y[-1])
    plt.plot(x, y, color='r', label='asks')
    if show:
        plt.show()


def find_wall(depth, multiplier=1000, val=None):
    """
    Find a buy or sell wall. Will search the depth until the qualifier is met.
    :param depth: side of order book (asks or bids)
    :param multiplier: classify wall by specified increase in size from one order to the next
    :param val: optionally classify wall by single value
    :return: wall order [price, size] or None if no wall found
    """
    if val is None:
        qualifier = lambda x: x * multiplier
    else:
        qualifier = lambda x: val

    for order in depth[1:]:
        if order[1] >= qualifier(depth[-1][1]):
            return order

    return None


def plot_price_and_walls(obs, **kwargs):
    """ Plots mid market price and wall positions/sizes """

    mmp = []
    buy_walls = []
    sell_walls = []
    for i, ob in enumerate(obs):
        mmp.append((ob['asks'][0][0] + ob['bids'][0][0]) / 2)
        o = find_wall(ob['asks'], **kwargs)
        if o is not None:
            sell_walls.append((i, o[0], o[1]))
        o = find_wall(ob['bids'], **kwargs)

        if o is not None:
            buy_walls.append((i, o[0], o[1]))

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    ax1.plot(mmp)

    if buy_walls:
        ax1.scatter([o[0] for o in buy_walls], [o[1] for o in buy_walls], marker='x', c='g')
    if sell_walls:
        ax1.scatter([o[0] for o in sell_walls], [o[1] for o in sell_walls], marker='x', c='r')

    ax2.bar([o[0] for o in buy_walls], [o[2] for o in buy_walls], color='g')
    ax3.bar([o[0] for o in sell_walls], [o[2] for o in sell_walls], color='r')
    plt.show()

def animate_depth(obs):
    """ Animated plot of depth over time """
    plt.ion()
    for ob in obs:
        plt.clf()
        plotdepth(ob)
        plt.pause(0.001)
    plt.ioff()

# def parsecsv(name):
#     df = pd.read_csv(name)
#     obs = []
#     for col in df:
#         if 'named' in col:
#             continue
#         if 'ask' in col:
#             ob = {'asks': [], 'bids': []}
#             for i in df[col].values:
#                 ob['asks'].append(ast.literal_eval(i))
#         elif 'bid' in col:
#             for i in df[col].values:
#                 ob['bids'].append(ast.literal_eval(i))
#             obs.append(ob)
#     return obs


if __name__ == "__main__":
    tracker = DepthTracker(num_snaps=600, interval=30, log_filename='venbtc')
    # tracker.track('VEN', 'BTC', ccxt.binance())
    tracker.load_log()
    obs = tracker.obs
    animate_depth(obs)
    # plotdepth(tracker.obs[0])
