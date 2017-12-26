import numpy as np
import operator
import warnings
# warnings.simplefilter('ignore')
from pyti.smoothed_moving_average import smoothed_moving_average as sma


class CoreBot:

    '''
        Responsible for step logic, short-term memory, and determining actions based on the rule set.
        Classes extending this must define:
            self.observable_funcs - dict of methods, defined within the class, that return values describing the current state
            self.action_funcs - dict of methods, defined within the class, that carry out thy bidding
    '''

    def __init__(self, funds, rule_set, memory_size=1024, verbose=False):

        self.funds = funds
        self.rule_set = rule_set
        self.positions = []  # Trade positions held
        self.verbose = verbose
        self.memory = {observable: [] for observable in self.observable_funcs.keys()}
        self.memory['price'] = []
        self.memory_size = memory_size

    def step(self, price):
        self.memorize('price', price)
        self.refresh_observables()
        action = self.decide_action()
        func = self.action_funcs[action]
        result = func()
        # print(self.memory)
        self.log('action: ' + action, details=result)

    def memorize(self, key, val):
        self.memory[key].append(val)
        if len(self.memory[key]) == self.memory_size:
            self.memory[key].pop(0)

    def refresh_observables(self):
        for observable, func in self.observable_funcs.items():
            val = func()
            self.memorize(observable, val)

    def decide_action(self):
        # Check current observables against rule set and return action
        ops = {
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '=': operator.eq
        }
        for item in self.rule_set:
            conditions_met = 0
            for condition in item['conditions']:
                observable = condition['observable']
                op, val = condition['value']
                op_func = ops[op]
                if op_func(self.memory[observable][-1], val):
                    conditions_met += 1
            if conditions_met == len(item['conditions']):
                return item['action']
        return 'wait'  # Default

    def log(self, message, details=None):
        if self.verbose:
            print(message)
        pass


class Bot(CoreBot):
    def __init__(self, *args, **kwargs):

        self.observable_funcs = {
            'n_positions': self.n_positions,
            'sma': self.smoothed_moving_average,
            'sma_gradient': self.smoothed_moving_average_gradient
        }
        self.action_funcs = {
            'wait': self.wait,
            'buy': self.buy,
            'sell': self.sell,
        }
        super().__init__(*args, **kwargs)

    ''' Observable functions '''

    def n_positions(self):
        return len(self.positions)

    def smoothed_moving_average(self, window_size=2):
        try:
            data = self.memory['price'][-window_size:]
            val = sma(np.array(data), window_size)[-1]
            return val
        except:  # Window size exceeds current memory
            return np.nan

    def smoothed_moving_average_gradient(self, window_size=2):
        try:
            val = np.gradient(self.memory['sma'][-window_size:])[-1]
            return val
        except:
            return np.nan

    ''' Action functions '''

    def buy(self):
        self.positions.append('yello')
        pass

    def sell(self):
        self.positions.pop(0)
        pass

    def wait(self):
        pass



if __name__ == '__main__':

    rule_set = [  # The first element in the rule set to have its conditions met has its action taken (i.e, order by precedence)
        {
            'action': 'wait',  # Action names correspond to bot.action_funcs
            'conditions': [  # If multiple conditions in list, all must be met
                {  # Each condition consists of an observable and a value check
                    'observable': 'n_positions',  # Observables correspond to values calculated at each step by bot.observable_funcs
                    'value': ('=', 1)
                }
            ]
        },
        {
            'action': 'buy',
            'conditions': [
                {
                    'observable': 'sma_gradient',
                    'value': ('>', 0.25)
                }
            ]
        },
        {
            'action': 'sell',
            'conditions': [
                {
                    'observable': 'n_positions',
                    'value': ('>=', 1)  # Must have one or more positions in order to sell
                },
                {
                    'observable': 'sma_gradient',
                    'value': ('<', -0.25)
                }
            ]
        }
    ]


    bot = Bot(100, rule_set, verbose=True)
    price_list = [5,8,3,6,5,7,4,6,5,10,15,15,15,15,15,3,2,1,0]
    for p in price_list:
        bot.step(p)