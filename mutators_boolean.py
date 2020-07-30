import options
from semantics import *

def is_not(node):
    return has_name(node) and get_name(node) == 'not'

def is_quantifier(node):
    return has_name(node) and get_name(node) in ['exists', 'forall']

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

class PassNegatedQuantifiers:
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
    options.disable_mutator_argument(argparser, 'negated-quant', 'push negations inside quantifiers')

def collect_mutators(args):
    res = []
    if args.mutator_boolean:
        res.append(PassDeMorgan())
        res.append(PassDoubleNegation())
        if args.mutator_eliminate_false_eq:
            res.append(PassEliminateFalseEquality())
        if args.mutator_negated_quant:
            res.append(PassNegatedQuantifiers())
    return res
