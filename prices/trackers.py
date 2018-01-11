from prices.snapshots import compare_two_exchanges, compare_order_books, compare_actual_market_prices
from private import CLIENTS
import time
import pandas as pd
import matplotlib.pyplot as plt
import os

class Tracker:
    """Short term price tracker"""
    def __init__(self, num_snaps=60, interval=60, log_filename=None):
        """
        Initialise tracker
        :param num_snaps: number of snapshots
        :param interval: interval between data points in seconds
        :param log_filename: path to log csvs (if None will not log csvs)
        """
        self.df = None
        self.num_snaps = num_snaps
        self.interval = interval
        if log_filename is not None:
            ext = '.csv' if not log_filename.endswith('.csv') else ''
            self.csv_path = '{}/data/{}{}'.format(os.path.dirname(os.path.abspath(__file__)), log_filename, ext)
        else:
            self.csv_path = None

    def load_csv(self, path=None):
        if path is None:
            path = self.csv_path
        self.df = pd.read_csv(path)

    def track(self):
        """Override"""
        pass

    def plot(self):
        for col in self.df:
            if 'named' in col:
                pass
            else:
                plt.plot(self.df[col].values, label=col)
        plt.xlabel('Interval')
        plt.ylabel('% difference')
        plt.legend()
        plt.show()


class CompareTwoExchangesTracker(Tracker):

    def __init__(self, num_snaps=60, interval=60, log_filename=None):
        super().__init__(num_snaps=num_snaps, interval=interval, log_filename=log_filename)

    def track(self, *args):
        """Input args for compare_two_exchanges() function"""
        base = [args[0]] if isinstance(args[0], str) else args[0]
        quote = [args[1]] if isinstance(args[1], str) else args[1]
        cols = []
        for b in base:
            for q in quote:
                cols.append(b + '-' + q)
        df = pd.DataFrame(columns=cols)

        for i in range(self.num_snaps):
            print('Snapshot: {}'.format(i))
            df2 = compare_two_exchanges(*args)
            row = {}
            for p in range(len(base)):
                name = df2.iloc[p]['Pair']
                val = df2.iloc[p]['% diff']
                row[name] = val
            df = df.append(row, ignore_index=True)
            time.sleep(self.interval)
            if self.csv_path is not None:
                df.to_csv(self.csv_path)
        self.df = df


class CompareOrderBooksTracker(Tracker):

    def __init__(self, num_snaps=60, interval=60, log_filename=None):
        super().__init__(num_snaps=num_snaps, interval=interval, log_filename=log_filename)

    def track(self, *args):
        """Input args for compare_order_books() function"""
        # not good yet
        base = [args[0]] if isinstance(args[0], str) else args[0]
        quote = [args[1]] if isinstance(args[1], str) else args[1]
        cols = []
        for b in base:
            for q in quote:
                cols.append(b + '-' + q)
        df = pd.DataFrame(columns=cols)

        for i in range(self.num_snaps):
            print('Snapshot: {}'.format(i))
            try:
                df2 = compare_order_books(*args)
            except:
                continue
            row = {}
            for p in range(len(base)):
                name = df2.iloc[p]['pair']
                val = df2.iloc[p]['% diff']
                row[name] = val
            df = df.append(row, ignore_index=True)
            time.sleep(self.interval)
            if self.csv_path is not None:
                df.to_csv(self.csv_path)
        self.df = df


class CompareActualMarketPricesTracker(Tracker):

    def __init__(self, num_snaps=60, interval=60, log_filename=None):
        super().__init__(num_snaps=num_snaps, interval=interval, log_filename=log_filename)

    def track(self, *args):
        df = compare_actual_market_prices(*args)
        base, quote = args[0], args[1]
        for i in range(self.num_snaps):
            print('Snapshot: {}'.format(i))
            time.sleep(self.interval)
            try:
                df = df.append(compare_actual_market_prices(*args), ignore_index=True)
            except:
                print('error')
                raise
                continue
            if self.csv_path is not None:
                df.to_csv(self.csv_path)
        self.df = df

    def plot(self):
        linestyles = ['-', '--', '-.', ':']
        i = 0
        for col in self.df:
            if 'named' in col or 'pair' in col:
                pass
            else:
                if col.endswith('buy'):
                    plt.plot(self.df[col], linestyle=linestyles[i], color='g', label=col)
                elif col.endswith('sell'):
                    plt.plot(self.df[col], linestyle=linestyles[i], color='r', label=col)
                    i += 1
        plt.legend()
        plt.show()


if __name__ == '__main__':
    tracker = CompareActualMarketPricesTracker(num_snaps=100, interval=30, log_filename='neoeth.csv')
    # tracker.track('NEO', 'ETH', 1000, (CLIENTS['Binance'], CLIENTS['Kucoin']))
    tracker.load_csv()
    tracker.plot()