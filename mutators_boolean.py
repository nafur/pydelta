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

class PassEliminateFalseEquality:
    """Replaces an equality with :code:`false` by a negation."""
    def filter(self, node):
        return not is_leaf(node) and len(node) == 3 and has_name(node) and get_name(node) == '=' and node[1] == 'false'
    def mutations(self, node):
        return [['not', node[2]]]
    def __str__(self):
        return 'replace equality with false by negation'

def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'boolean', 'boolean mutators')
    options.disable_mutator_argument(argparser, 'eliminate-false-eq', 'eliminate equalities with false')

def collect_mutators(args):
    res = []
    if args.mutator_boolean:
        if args.mutator_eliminate_false_eq:
            res.append(PassEliminateFalseEquality())
    return res
