import operator
import warnings
from datetime import datetime
# warnings.simplefilter('ignore')
import numpy as np


class CoreBot:

    '''
        Responsible for
            step logic,
            short-term memory,
            determining actions based on the rule set,
            keeping funds and trading positions up to date,
            interfacing with trading client/s,
            logging
        Classes extending this must define:
            self.observable_funcs - dict of methods, defined within the class, that return values describing the current state
            self.action_funcs - dict of methods, defined within the class, that carry out thy bidding
    '''

    def __init__(self, funds, rule_set, memory_size=1024, verbose=False):
        self.funds = funds
        # fee_coeff here
        self.rule_set = rule_set
        self.positions = []  # Trade positions held
        self.verbose = verbose
        self.memory_size = memory_size
        self.memory = {}
        if not 'wait' in self.action_funcs:
            self.action_funcs['wait'] = lambda: {}

    def step(self, price):
        self.memorize('price', price)
        self.refresh_observables()
        action = self.decide_action()
        func = self.action_funcs[action]
        result = func()  # Action methods return details about the action
        result.update({'action': action, 'timestamp': datetime.now()})
        self.memorize('action', result)
        self.log('action: ' + action, details=result)

    def memorize(self, key, val):
        try:
            self.memory[key].append(val)
        except:
            self.memory[key] = [val]
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

    def trade(self, type=None, with_funds=None):
        current_price = self.memory['price'][-1]

        if type == 'buy':
            assert with_funds, 'Must provide with_funds if buying'
            self.funds -= with_funds
            amount = with_funds / current_price
            position = {
                'price': current_price,
                'invested': with_funds,
                'amount': amount}
            self.positions.append(position)
            return position

        if type == 'sell':
            position = self.positions[0]  # For now assume only one position held
            relinquished = position['amount'] * current_price
            self.funds += relinquished
            self.positions.pop(0)
            result = {
                'price': current_price,
                'amount': position['amount'],
                'relinquished': relinquished,
                'net': relinquished - position['invested']}
            return result

    def log(self, message, details=None, ignore_wait=True):
        if ignore_wait:
            try:
                if details['action'] == 'wait':
                    return
            except: pass
        if self.verbose:
            # print(message)
            print(details)
            # for key, val in details.items():
                # print(key, ': ', val)



class Bot(CoreBot):
    def __init__(self, *args, **kwargs):

        self.observable_funcs = {
            'n_positions': lambda: len(self.positions),
            'sma10': lambda: self.sma(window_size=10),
            'sma45': lambda: self.sma(window_size=45),
            'sma10_gradient': lambda: self.gradient('sma10', window_size=10),
            'sma45_gradient': lambda: self.gradient('sma45', window_size=45),
        }
        self.action_funcs = {
            'buy': self.buy,
            'sell': self.sell,
        }
        super().__init__(*args, **kwargs)

    ''' Observables '''

    def sma(self, window_size=60):
        try:
            data = self.memory['price'][-window_size:]
            val = np.mean(np.array(data))
            return val
        except IndexError as e:  # Window size exceeds current memory
            return np.nan

    def gradient(self, observable, window_size=60):
        try:
            val = np.gradient(self.memory[observable][-window_size:])[-1]
            return val
        except IndexError as e:
            pass
        except ValueError as e:
            pass
        except KeyError as e:
            print('Warning: observable does not exist')
            pass
        return np.nan

    ''' Actions '''

    def buy(self):
        with_funds = self.funds * 0.1  # Trade a 10th of what we have
        result = self.trade(type='buy', with_funds=with_funds)  # Other params like stoploss etc.
        return result

    def sell(self):
        result = self.trade(type='sell')
        # Profit scraping here for example
        return result


if __name__ == '__main__':

    example_rule_set = [  # The first element in the rule set to have its conditions met has its action taken (i.e, order by precedence)
        {
            'action': 'buy',  # Action names correspond to bot.action_funcs
            'conditions': [  # If multiple conditions in list, all must be met
                {  # Each condition consists of an observable and a value check
                    'observable': 'sma_gradient',  # Observables correspond to values calculated at each step by bot.observable_funcs
                    'value': ('>', 2)
                },
                {
                    'observable': 'n_positions',
                    'value': ('<', '1')  # Only want one position active
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
                    'value': ('<', -2)
                }
            ]
        }
    ]

    bot = Bot(100, example_rule_set, verbose=True)
    data = [5, 8, 3, 6, 5, 7, 4, 6, 5, 10, 15, 15, 15, 15, 15, 3, 2, 1, 0]
    for d in data:
        bot.step(d)
