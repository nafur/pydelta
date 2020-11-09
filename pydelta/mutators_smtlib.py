from . import options
from .semantics import *

NAME = 'smtlib'
MUTATORS = ['check-sat-assuming', 'push-pop-removal']

class PassCheckSatAssuming:
    """Replaces a :code:`check-sat-assuming` by a regular :code:`check-sat`."""
    def filter(self, node):
        return has_name(node) and get_name(node) == 'check-sat-assuming'
    def mutations(self, node):
        return [['check-sat']]
    def __str__(self):
        return 'substitute check-sat-assuming by check-sat'

class PassSimplifyLogic:
    """Replaces the logic specified in :code`(check-logic ...)` by a simpler one."""
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

class PassPushPopRemoval:
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
        return 'remove push-pop pairs'

def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'smtlib mutators')
    options.add_mutator_argument(argparser, 'check-sat-assuming', True, 'replace check-sat-assuming by check-sat')
    options.add_mutator_argument(argparser, 'push-pop-removal', True, 'remove push-pop pairs')
    options.add_mutator_argument(argparser, 'simplify-logic', True, 'simplify declared logic')

def collect_mutators(args):
    res = []
    if args.mutator_smtlib:
        if args.mutator_check_sat_assuming:
            res.append(PassCheckSatAssuming())
        if args.mutator_push_pop_removal:
            res.append(PassPushPopRemoval())
        if args.mutator_simplify_logic:
            res.append(PassSimplifyLogic())
    return res
