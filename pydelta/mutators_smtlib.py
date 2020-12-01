import re

from . import options
from .semantics import *

NAME = 'smtlib'
MUTATORS = [
    'check-sat-assuming', 'eliminate-distinct', 'inline-functions', 'let-elimination',
    'let-substitution', 'push-pop-removal', 'simplify-logic', 'simplify-quoted-symbol', 'variable-names'
]

class CheckSatAssuming:
    """Replaces a :code:`check-sat-assuming` by a regular :code:`check-sat`."""
    def filter(self, node):
        return has_name(node) and get_name(node) == 'check-sat-assuming'
    def mutations(self, node):
        return [['check-sat']]
    def __str__(self):
        return 'substitute check-sat-assuming by check-sat'

class EliminateDistinct:
    """Replaces distinct by a negated equality."""
    def filter(self, node):
        return has_name(node) and get_name(node) == 'distinct'
    def mutations(self, node):
        return [['not', ['='] + node[1:]]]
    def __str__(self):
        return 'eliminate distinct'

class InlineDefinedFuns:
    """Explicitly inlines a defined function."""
    def filter(self, node):
        return is_defined_function(node)
    def mutations(self, node):
        return [ get_defined_function(node) ]
    def __str__(self):
        return 'inline defined function'

class LetElimination:
    """Substitutes a :code:`let` expression with its body."""
    def filter(self, node):
        return is_let(node)
    def mutations(self, node):
        return [node[2]]
    def __str__(self):
        return 'eliminate let binder'

class LetSubstitution:
    """Substitutes a variable bound by a :code:`let` binder into the nested term."""
    def filter(self, node):
        return is_let(node)
    def mutations(self, node):
        res = []
        for var in node[1]:
            if contains(node[2], var[0]):
                subs = substitute(node[2], {var[0]: var[1]})
                res.append([node[0], node[1], subs])
        return res
    def __str__(self):
        return 'substitute variable into let body'

class PushPopRemoval:
    """Removes matching :code:`(push)(pop)` pairs. First tries successive pairs, distant ones later."""
    def filter(self, node):
        return not has_name(node)
    def mutations(self, node):
        res = []
        pairs = []
        # identify (push) / (pop) pairs
        stack = []
        for i in range(len(node)):
            if node[i] == ['push']:
                stack.append(i)
            if node[i] == ['pop'] and stack != []:
                pairs.append((stack[-1], i))
                stack.pop()
        # remove directly successive pairs
        for p in pairs:
            if p[0]+1 == p[1]:
                i = p[0]
                res.append(node[:i] + node[i+2:])
        if res != []:
            return res
        # remove non-successive pairs
        for p in pairs:
            r = node[:p[0]] + node[p[0]+1:p[1]] + node[p[1]+1:]
            res.append(r)
        return res
    def __str__(self):
        return 'remove push-pop pair'
class SimplifyLogic:
    """Replaces the logic specified in :code:`(check-logic ...)` by a simpler one."""
    def filter(self, node):
        return has_name(node) and get_name(node) == 'set-logic'
    def mutations(self, node):
        logic = node[1]
        cands = []
        repls = { 'BV': '', 'FP': '', 'UF': '', 'S': '', 'T': '', 'NRA': 'LRA' }
        for r in repls:
            if r in logic:
                cands.append(logic.replace(r, repls[r]))
        return [['set-logic', c] for c in cands]
    def __str__(self):
        return 'simplify logic'

class SimplifyQuotedSymbol:
    """Turns a quoted symbol into a simple symbol."""
    def filter(self, node):
        return is_quoted_symbol(node) and re.match('|[a-zA-Z0-9~!@$%^&*_+=<>.?/-]+|', node) is not None
    def global_mutations(self, linput, ginput):
        return [ substitute(ginput, { linput: get_quoted_symbol(linput) }) ]
    def __str__(self):
        return 'simplify quoted symbol'

class VariableNames:
    """Simplify variable names."""
    def filter(self, node):
        return has_name(node) and get_name(node) in ['declare-const', 'declare-fun']
    def global_mutations(self, linput, ginput):
        name = linput[1]
        repl = lambda s: {linput[1]: s}
        if is_quoted_symbol(name):
            name = get_quoted_symbol(linput[1])
            repl = lambda s: {linput[1]: '|' + s + '|'}
        return [
            substitute(ginput, repl(s)) for s in self.__simpler(name)
        ]
    def __simpler(self, name):
        if len(name) < 2:
            return []
        half = len(name) // 2
        return [name[:half], name[:-1]]
    def __str__(self):
        return 'simplify variable name'

def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'smtlib mutators')
    options.add_mutator_argument(argparser, 'check-sat-assuming', True, 'replace check-sat-assuming by check-sat')
    options.add_mutator_argument(argparser, 'eliminate-distinct', True, 'eliminate distinct by negated equalities')
    options.add_mutator_argument(argparser, 'inline-functions', True, 'inline defined functions')
    options.add_mutator_argument(argparser, 'let-elimination', True, 'eliminate let bindings')
    options.add_mutator_argument(argparser, 'let-substitution', True, 'substitute bound variables in let bindings')
    options.add_mutator_argument(argparser, 'push-pop-removal', True, 'remove push-pop pairs')
    options.add_mutator_argument(argparser, 'simplify-logic', True, 'simplify declared logic')
    options.add_mutator_argument(argparser, 'simplify-quoted-symbol', False, 'simplify quoted symbols')
    options.add_mutator_argument(argparser, 'variable-names', False, 'simplify variable names')

def collect_mutators(args):
    res = []
    if args.mutator_smtlib:
        if args.mutator_check_sat_assuming:
            res.append(CheckSatAssuming())
        if args.mutator_eliminate_distinct:
            res.append(EliminateDistinct())
        if args.mutator_inline_functions:
            res.append(InlineDefinedFuns())
        if args.mutator_let_elimination:
            res.append(LetElimination())
        if args.mutator_let_substitution:
            res.append(LetSubstitution())
        if args.mutator_push_pop_removal:
            res.append(PushPopRemoval())
        if args.mutator_simplify_logic:
            res.append(SimplifyLogic())
        if args.mutator_simplify_quoted_symbol:
            res.append(SimplifyQuotedSymbol())
        if args.mutator_variable_names:
            res.append(VariableNames())
    return res
