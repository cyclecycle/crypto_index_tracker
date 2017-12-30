import os
import sys
from pathlib import Path
import operator
import warnings
from datetime import datetime
# warnings.simplefilter('ignore')
import numpy as np
from functools import partial
import yaml

ROOT = Path(os.path.dirname(os.path.realpath(__file__))).parents[0]
sys.path.insert(0, str(ROOT))
import helpers

RULE_SET_DIR = os.path.join(ROOT, 'trade/rule_sets')

from indicators import Indicators


class CoreBot:

    '''
        Responsible for
            reading the rule set,
            step logic,
            short-term memory,
            determining actions based on the rule set,
            keeping funds and trading positions up to date,
            interfacing with trading client/s OR simulating trading,
            logging
    '''

    def __init__(self, rule_set=None, funds=100, memory_size=1024, verbose=False):

        self.funds = funds
        self.positions = []  # Trade positions held
        self.memory = {}  # Keep a limited history of observables and actions taken
        self.memory_size = memory_size  # Number of memory slots
        self.verbose = verbose

        ''' Initialise rule set '''
        if rule_set:
            self.raw_rule_set = rule_set
            self.init_rule_set()
            self.init_observables()
            self.init_actions()

    ''' Core '''

    def step(self, **inputs):
        for k, v in inputs.items():
            self.memorize(k, v)
        self.refresh_observables()
        action = self.decide_action()
        func = self.action_funcs[action]
        result = func()  # Action methods return details about the action
        result.update({'action': action, 'timestamp': datetime.now()})
        self.memorize('action', result)
        self.memorize('funds', self.funds)
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
        ''' Check current observables against rule set and return action '''
        ops = {
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '=': operator.eq
        }
        for rule in self.rule_set['rules']:
            conditions_met = 0
            for condition in rule['conditions']:
                observable = condition['observable']
                op, val = condition['value']
                op_func = ops[op]
                if op_func(self.memory[observable][-1], val):
                    conditions_met += 1
            if conditions_met == len(rule['conditions']):
                return rule['action']
        return self.default_action

    def trade(self, _type, with_funds=None):
        ''' If no trading client, it's a simulation '''

        current_price = self.memory['price'][-1]

        if _type == 'buy':
            assert with_funds, 'Must provide with_funds if buying'
            self.funds -= with_funds
            amount = with_funds / current_price
            position = {
                'price': current_price,
                'invested': with_funds,
                'amount': amount}
            self.positions.append(position)
            return position

        if _type == 'sell':
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

    ''' Convenience methods '''

    def load_rule_set(self, filename):
        with open(os.path.join(RULE_SET_DIR, filename)) as f:
            self.raw_rule_set = yaml.load(f)
        self.init_rule_set()
        self.init_observables()
        self.init_actions()

    def init_rule_set(self):
        ''' Substitute variables defined in rule set '''
        new_rule_set = self.raw_rule_set.copy()
        del new_rule_set['vars']
        self.rule_set = helpers.recursive_replace(new_rule_set, self.raw_rule_set['vars'])
        ''' Set default action '''
        try:
            self.default_action = self.rule_set['rules']['default']
            del self.rule_set['rules']['default']
        except:
            self.default_action = 'wait'

    def init_observables(self):
        self.observable_funcs = self.init_method_dict(self.rule_set['observables'])
        if not 'n_positions' in self.observable_funcs:
            self.observable_funcs['n_positions'] = lambda: len(self.positions)

    def init_actions(self):
        self.action_funcs = self.init_method_dict(self.rule_set['actions'])
        if not 'wait' in self.action_funcs:
            self.action_funcs['wait'] = lambda: {}

    def init_method_dict(self, dict_from_rule_set):
        method_dict = {}
        for key, vals in dict_from_rule_set.items():
            func = self.__getattribute__(vals['func'])  # Get the method
            args = vals.get('args', [])
            kwargs = vals.get('kwargs', {})
            func = partial(func, *args, **kwargs)  # Construct the new callable
            method_dict[key] = func
        return method_dict

    def current_state(self, with_timestamp=False):
        ''' Gives latest values in memory for debugging / logging purposes '''
        state = {k: vals[-1] for k, vals in self.memory.items()}
        if with_timestamp:
            state.update({'timestamp': datetime.now()})
        if self.verbose:
            for k, v in state.items():
                print('\n', k + ':', v, end='\r')
        return state

    def log(self, message, details=None, ignore_wait=True):
        if ignore_wait:
            try:
                if details['action'] == 'wait':
                    return
            except: pass
        if self.verbose:
            for k, v in details.items():
                print('\n', k + ':', v, end='\r')


class Bot(CoreBot, Indicators):

    def buy(self, with_funds_frac=0.1):
        with_funds = self.funds * with_funds_frac
        result = self.trade('buy', with_funds=with_funds)  # Other params like stoploss etc.
        return result


if __name__ == '__main__':

    bot = Bot(funds=1000, verbose=True)
    bot.load_rule_set('rs2.yaml')
    price_list = [5, 8, 3, 6, 5, 7, 4, 6, 5, 10, 15, 15, 15, 15, 15, 3, 2, 1, 0]
    for p in price_list:
        inputs = {'price': p, 'other_info': 123}
        bot.step(**inputs)
