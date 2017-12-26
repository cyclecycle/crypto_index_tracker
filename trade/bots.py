from private import CLIENTS  # Dict of ccxt clients instantiated with private API keys
import ccxt
import numpy as np
import matplotlib.pyplot as plt


class SMALimBot:

    def __init__(self, funds=100, frac=0.01, mov_avg_len=60):
        self.funds = funds
        self.size = 0
        self.val = funds
        self.lim = None
        self.lim_frac = frac
        self.fee_coeff = 1 - 0.003
        self.mov_avg = []
        self.mov_avg_len = mov_avg_len

        self.trades = []

        self.set_lim(99, 'buy')

    def step(self, P):
        self.P = P
        self.set_movavg()
        self.update_lim()
        self.update_val()

    def update_lim(self):
        p = self.P[-1]
        if self.lim is not None:
            if self.lim[1] == 'buy':
                if self.lim[0] > p:
                    self.size += (self.funds / p) * self.fee_coeff
                    self.trades.append(('buy', self.funds, self.size, p, len(self.P) - self.mov_avg_len))
                    self.funds = 0
                    self.set_lim((1 + self.lim_frac) * self.mov_avg[-1], 'sell')
            elif self.lim[1] == 'sell':
                if self.lim[0] < p:
                    self.funds += p * self.size * self.fee_coeff
                    self.trades.append(('sell', self.funds, self.size, p, len(self.P) - self.mov_avg_len))
                    self.size = 0
                    self.set_lim((1 - self.lim_frac) * self.mov_avg[-1], 'buy')

    def update_val(self):
        self.val = self.funds + self.P[-1] * self.size

    def set_movavg(self):
        assert len(self.P) > self.mov_avg_len
        self.mov_avg.append(np.mean(self.P[-self.mov_avg_len:]))

    def set_lim(self, lim, type):
        self.lim = (lim, type)

    def plot(self):
        plt.plot(self.P[self.mov_avg_len:])
        plt.plot(self.mov_avg)

        if self.trades:
            xb, yb, xs, ys = [], [], [], []
            for t in self.trades:
                if t[0] == 'buy':
                    xb.append(t[4])
                    yb.append(t[3])
                elif t[0] == 'sell':
                    xs.append(t[4])
                    ys.append(t[3])
        plt.scatter(xb, yb, c='g', marker='x')
        plt.scatter(xs, ys, c='r', marker='x')
        plt.show()


if __name__ == '__main__':
    pass
