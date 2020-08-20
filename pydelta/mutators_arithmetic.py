from . import options
from .semantics import *

NAME = 'arithmetic'
MUTATORS = ['arith-constants', 'arith-negate-relations']

def is_arithmetic_relation(node):
    if not has_name(node):
        return False
    return get_name(node) in ['=', '<', '>', '>=', '<=', '!=', '<>']

class PassArithmeticSimplifyConstant:
    """Replace a constant by a simpler version (smaller or fewer decimal places)."""
    def filter(self, node):
        return is_arithmetic_constant(node) and float(node) not in [0, 1]
    def mutations(self, node):
        f = float(node)
        if int(f) == f:
            i = int(f)
            return [str(i // 2), str(i // 10)]
        return [str(int(f)), node[:-1]]
    def __str__(self):
        return 'simplify arithmetic constant'

class PassArithmeticNegateRelations:
    """Replace a constant by a simpler version (smaller or fewer decimal places)."""
    def filter(self, node):
        return is_not(node) and is_arithmetic_relation(node[1])
    def mutations(self, node):
        negator = { '<': '>=', '<=': '>', '!=': '=', '<>': '=', '>=': '<', '>': '<=' }
        if node[1][0] in negator:
            return [[negator[node[1][0]]] + node[1][1:]]
        return []
    def __str__(self):
        return 'push negations into relations'

class PassArithmeticStrengthenRelations:
    """Replace a relation by a stronger relation."""
    def filter(self, node):
        return is_arithmetic_relation(node)
    def mutations(self, node):
        negator = { '<': ['='], '>': ['='], '<=': ['<', '='], '>=': ['>', '='] }
        if node[0] in negator:
            return [[rel] + node[1:] for rel in negator[node[0]]]
        return []
    def __str__(self):
        return 'strengthen relation'

def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'arithmetic mutators')
    options.add_mutator_argument(argparser, 'arith-constants', True, 'replaces constants by simpler ones')
    options.add_mutator_argument(argparser, 'arith-negate-relations', True, 'push negations inside of relations')
    options.add_mutator_argument(argparser, 'arith-strengthen-relations', True, 'strengthen relations')

def collect_mutators(args):
    res = []
    if args.mutator_arithmetic:
        if args.mutator_arith_constants:
            res.append(PassArithmeticSimplifyConstant())
        if args.mutator_arith_negate_relations:
            res.append(PassArithmeticNegateRelations())
        if args.mutator_arith_strengthen_relations:
            res.append(PassArithmeticStrengthenRelations())
    return res
