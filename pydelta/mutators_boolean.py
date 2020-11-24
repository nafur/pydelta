from . import options
from .semantics import *

NAME = 'boolean'
MUTATORS = ['eliminate-false-eq', 'negate-quant']

def is_quantifier(node):
    return has_name(node) and get_name(node) in ['exists', 'forall']

class DeMorgan:
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

class DoubleNegation:
    """Elimination double negations."""
    def filter(self, node):
        return is_not(node) and is_not(node[1])
    def mutations(self, node):
        return [node[1][1]]
    def __str__(self):
        return 'eliminate double negation'

class EliminateFalseEquality:
    """Replaces an equality with :code:`false` by a negation."""
    def filter(self, node):
        return not is_leaf(node) and len(node) == 3 and has_name(node) and get_name(node) == '=' and node[1] == 'false'
    def mutations(self, node):
        return [['not', node[2]]]
    def __str__(self):
        return 'replace equality with false by negation'

class EliminateImplications:
    """Replaces implications by disjunctions."""
    def filter(self, node):
        return has_name(node) and get_name(node) == '=>' and len(node) == 3
    def mutations(self, node):
        return [['or', ['not', node[1]], node[2]]]
    def __str__(self):
        return 'eliminate implication'

class NegatedQuantifiers:
    """Pushes negation inside quantifiers."""
    def filter(self, node):
        return is_not(node) and is_quantifier(node[1])
    def mutations(self, node):
        if get_name(node[1]) == 'exists':
            return [['forall', node[1][1], ['not', node[1][2]]]]
        if get_name(node[1]) == 'forall':
            return [['exists', node[1][1], ['not', node[1][2]]]]
        return []
    def __str__(self):
        return 'push negation inside of quantifier'

def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'boolean mutators')
    options.add_mutator_argument(argparser, 'de-morgan', True, 'apply de Morgan to push negations inside')
    options.add_mutator_argument(argparser, 'double-negations', True, 'eliminate double negations')
    options.add_mutator_argument(argparser, 'eliminate-false-eq', True, 'eliminate equalities with false')
    options.add_mutator_argument(argparser, 'eliminate-implications', True, 'eliminate equalities with false')
    options.add_mutator_argument(argparser, 'negated-quant', True, 'push negations inside quantifiers')

def collect_mutators(args):
    res = []
    if args.mutator_boolean:
        if args.mutator_de_morgan:
            res.append(DeMorgan())
        if args.mutator_double_negations:
            res.append(DoubleNegation())
        if args.mutator_eliminate_false_eq:
            res.append(EliminateFalseEquality())
        if args.mutator_eliminate_implications:
            res.append(EliminateImplications())
        if args.mutator_negated_quant:
            res.append(NegatedQuantifiers())
    return res
