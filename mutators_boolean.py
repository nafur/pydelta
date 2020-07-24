import options
from semantics import *

def is_boolean(node):
    """Checks whether the :code:`node` is Boolean."""
    if node in ['false', 'true']:
        return True
    if has_type(node):
        return get_type(node) in ['Bool']
    if is_ite(node):
        return is_boolean(node[1])
    if has_name(node):
        return get_name(node) in [
            # core theory
            'not', '=>', 'and', 'or', 'xor', '=', 'distinct'
            '<', '<=', '>', '>=',
            # set theory
            'member',
        ]
    return False

def is_not(node):
    return has_name(node) and get_name(node) == 'not'

class PassEliminateFalseEquality:
    """Replaces an equality with :code:`false` by a negation."""
    def filter(self, node):
        return not is_leaf(node) and len(node) == 3 and has_name(node) and get_name(node) == '=' and node[1] == 'false'
    def mutations(self, node):
        return [['not', node[2]]]
    def __str__(self):
        return 'replace equality with false by negation'

class PassDeMorgan:
    """Uses de Morgans rules to push negations inside."""
    def filter(self, node):
        return is_not(node) and has_name(node[1])
    def mutations(self, node):
        if get_name(node[1]) == 'and':
            res = [['not', t] for t in node[1][1:]]
            return [['or', *res]]
        if get_name(node[1]) == 'or':
            res = [['not', t] for t in node[1][1:]]
            return [['and', *res]]
        return []
    def __str__(self):
        return 'push negation inside'

class PassDoubleNegation:
    """Elimination double negations."""
    def filter(self, node):
        return is_not(node) and is_not(node[1])
    def mutations(self, node):
        return [node[1][1]]
    def __str__(self):
        return 'eliminate double negation'

def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'boolean', 'boolean mutators')
    options.disable_mutator_argument(argparser, 'eliminate-false-eq', 'eliminate equalities with false')

def collect_mutators(args):
    res = []
    if args.mutator_boolean:
        res.append(PassDeMorgan())
        res.append(PassDoubleNegation())
        if args.mutator_eliminate_false_eq:
            res.append(PassEliminateFalseEquality())
    return res
