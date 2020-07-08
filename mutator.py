import copy
import logging
import parser
import progressbar

from semantics import *

class PassEraseChildren:
    def filter(self, node):
        return isinstance(node, list)
    def mutations(self, node):
        res = []
        for i in range(len(node)):
            tmp = node.copy()
            del tmp[i]
            res.append(tmp)
        return res
    def __str__(self):
        return 'erase children'

class PassSubstituteChildren:
    def filter(self, node):
        return isinstance(node, list)
    def mutations(self, node):
        return node
    def __str__(self):
        return 'substitute with children'

class PassConstant:
    def __init__(self, f, constant):
        self.__filter = f
        self.__constant = constant
    def filter(self, node):
        return self.__filter(node)
    def mutations(self, node):
        return [self.__constant]
    def __str__(self):
        return 'substitute by constant \"{}\"'.format(self.__constant)

class PassLetSubstitution:
    def filter(self, node):
        return is_let(node) and not is_empty_let(node)
    def mutations(self, node):
        res = []
        print(node)
        for varid in range(len(node[1])):
            var = node[1][varid]
            subs = substitute(node[2], {var[0]: var[1]})
            res.append([node[0], node[1][:varid] + node[1][varid + 1:], subs])
        print(res)
        return res
    def __str__(self):
        return 'substitute variable into let body'

class PassLetElimination:
    def filter(self, node):
        return is_empty_let(node)
    def mutations(self, node):
        return [node[2]]
    def __str__(self):
        return 'substitute let with body'

class PassInlineDefinedFuns:
    def filter(self, node):
        return is_defined_function(node)
    def mutations(self, node):
        return [ get_defined_function(node)(node[1:]) ]
    def __str__(self):
        return 'inline defined functions'

def add_mutator_argument(argparser, option, name, action, help):
    dest = 'mutator_{}'.format(name.replace('-', '_'))
    argparser.add_argument(option, dest = dest, action = action, help = help)
def enable_mutator_argument(argparser, name, help):
    add_mutator_argument(argparser, '--with-{}'.format(name), name, 'store_true', help)
def disable_mutator_argument(argparser, name, help):
    add_mutator_argument(argparser, '--without-{}'.format(name), name, 'store_false', help)
    
def collect_mutator_options(argparser):
    disable_mutator_argument(argparser, 'erase-children', 'erase individual children of nodes')
    disable_mutator_argument(argparser, 'substitute-children', 'substitute nodes with their children')
    disable_mutator_argument(argparser, 'inline-functions', 'inline defined functions')
    disable_mutator_argument(argparser, 'eliminate-lets', 'eliminate let bindings')
    disable_mutator_argument(argparser, 'constant-false', 'replace nodes by false')
    disable_mutator_argument(argparser, 'constant-true', 'replace nodes by true')
    disable_mutator_argument(argparser, 'constant-zero', 'replace nodes by zero')
    disable_mutator_argument(argparser, 'constant-one', 'replace nodes by one')

enabled_mutators = []
def collect_mutators(args):
    global enabled_mutators
    enabled_mutators.append(PassInlineDefinedFuns())
    if args.mutator_erase_children:
        enabled_mutators.append(PassEraseChildren())
    if args.mutator_substitute_children:
        enabled_mutators.append(PassSubstituteChildren())
    if args.mutator_inline_functions:
        enabled_mutators.append(PassInlineDefinedFuns())
    if args.mutator_eliminate_lets:
        enabled_mutators.append(PassLetSubstitution())
        enabled_mutators.append(PassLetElimination())
    if args.mutator_constant_false:
        enabled_mutators.append(PassConstant(lambda n: not is_boolean_constant(n) and is_boolean(n), 'false'))
    if args.mutator_constant_true:
        enabled_mutators.append(PassConstant(lambda n: not is_boolean_constant(n) and is_boolean(n), 'true'))
    if args.mutator_constant_zero:
        enabled_mutators.append(PassConstant(lambda n: not is_arithmetic_constant(n) and is_arithmetic(n), '0'))
    if args.mutator_constant_one:
        enabled_mutators.append(PassConstant(lambda n: not is_arithmetic_constant(n) and is_arithmetic(n), '1'))

def mutate_node(node):
    res = []
    for m in enabled_mutators:
        if hasattr(m, 'filter') and not m.filter(node):
            continue
        res = res + list(map(lambda x: (str(m), x), m.mutations(node)))
    return res


def __generate_mutations(input, prg):
    prg.update(prg.currval + 1)
    yield from mutate_node(input)
    if isinstance(input, list):
        for i in range(len(input)):
            cand = copy.copy(input)
            for mutated in __generate_mutations(input[i], prg):
                cand[i] = mutated[1]
                yield (mutated[0], cand)

def generate_mutations(input):
    collect_information(input)
    s = node_count(input)
    widgets = [progressbar.Bar(), ' ', progressbar.Counter(), ' / ', str(s)]
    prg = progressbar.ProgressBar(maxval = s, widgets = widgets)
    prg.start()
    yield from __generate_mutations(input, prg)
