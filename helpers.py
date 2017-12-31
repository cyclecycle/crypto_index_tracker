import os

ROOT = os.path.dirname(os.path.realpath(__file__))


def recursive_replace(item, repl_dict):
    ''' Recursively replace key / vars '''
    if isinstance(item, str):
        for k, v in repl_dict.items():
            if k == item:
                return repl_dict[k]
        return item
    elif isinstance(item, dict):
        return {recursive_replace(k, repl_dict): recursive_replace(v, repl_dict) for k, v in item.items()}
    elif isinstance(item, list):
        return [recursive_replace(el, repl_dict) for el in item]
    else:
        return item