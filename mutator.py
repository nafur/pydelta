import copy
import logging
import progressbar

import mutators_arithmetic
import mutators_bitvectors
import mutators_boolean
import mutators_core
from semantics import *

def collect_mutator_options(argparser):
    mutators_core.collect_mutator_options(argparser.add_argument_group('core mutator arguments'))
    mutators_boolean.collect_mutator_options(argparser.add_argument_group('boolean mutator arguments'))
    mutators_arithmetic.collect_mutator_options(argparser.add_argument_group('arithmetic mutator arguments'))
    mutators_bitvectors.collect_mutator_options(argparser.add_argument_group('bitvector mutator arguments'))

enabled_mutators = []
def collect_mutators(args):
    global enabled_mutators
    enabled_mutators += mutators_core.collect_mutators(args)
    enabled_mutators += mutators_boolean.collect_mutators(args)
    enabled_mutators += mutators_arithmetic.collect_mutators(args)
    enabled_mutators += mutators_bitvectors.collect_mutators(args)

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
