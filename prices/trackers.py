from prices.snapshots import compare_two_exchanges
import time
import pandas as pd
import matplotlib.pyplot as plt

class Tracker:
    """Short term price tracker"""
    def __init__(self, num_snaps=60, interval=60, csv_log_path=None):
        """
        Initialise tracker
        :param num_snaps: number of snapshots
        :param interval: interval between data points in seconds
        :param csv_log_path: path to log csvs (if None will not log csvs)
        """
        self.df = None
        self.num_snaps = num_snaps
        self.interval = interval
        if csv_log_path is not None:
            self.csv_path = csv_log_path

    def load_csv(self, path):
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

    def __init__(self, num_snaps=60, interval=60, csv_log_path=None):
        super().__init__(num_snaps=num_snaps, interval=interval, csv_log_path=csv_log_path)

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
            df2 = compare_two_exchanges(*args)
            row = {}
            for p in range(len(base)):
                name = df2.iloc[p]['Pair']
                val = df2.iloc[p]['% diff']
                row[name] = val
            df = df.append(row, ignore_index=True)
            time.sleep(self.interval)
            if self.csv_path is not None:
                df.to_csv('data/{}.csv'.format(self.csv_path))
        self.df = df


if __name__ == '__main__':
    tracker = CompareTwoExchangesTracker(csv_log_path='data/tracker.csv')
    tracker.load_csv('data/krakenarb.csv')
    tracker.plot()