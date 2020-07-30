import copy
import logging
import progressbar

import mutators_arithmetic
import mutators_bitvectors
import mutators_boolean
import mutators_core
import mutators_smtlib
import mutators_strings
import semantics

def collect_mutator_options(argparser):
    """Adds all options related to mutators to the given argument parser."""
    mutators_core.collect_mutator_options(argparser.add_argument_group('core mutator arguments'))
    mutators_boolean.collect_mutator_options(argparser.add_argument_group('boolean mutator arguments'))
    mutators_arithmetic.collect_mutator_options(argparser.add_argument_group('arithmetic mutator arguments'))
    mutators_bitvectors.collect_mutator_options(argparser.add_argument_group('bitvector mutator arguments'))
    mutators_smtlib.collect_mutator_options(argparser.add_argument_group('smtlib mutator arguments'))
    mutators_strings.collect_mutator_options(argparser.add_argument_group('strings mutator arguments'))

enabled_mutators = []
def collect_mutators(args):
    """Initializes the list of all active mutators."""
    global enabled_mutators
    enabled_mutators += mutators_core.collect_mutators(args)
    enabled_mutators += mutators_boolean.collect_mutators(args)
    enabled_mutators += mutators_arithmetic.collect_mutators(args)
    enabled_mutators += mutators_bitvectors.collect_mutators(args)
    enabled_mutators += mutators_smtlib.collect_mutators(args)
    enabled_mutators += mutators_strings.collect_mutators(args)

def __mutate_node(node):
    """Apply all active mutators to the given node. Returns a list of all possible mutations."""
    res = []
    for m in enabled_mutators:
        if hasattr(m, 'filter') and not m.filter(node):
            continue
        res = res + list(map(lambda x: (str(m), x), m.mutations(node)))
    return res


def __generate_mutations(input, prg):
    """Generate mutations from the given input, updating the progress bar."""
    prg.update(prg.currval + 1)
    yield from __mutate_node(input)
    if isinstance(input, list):
        for i in range(len(input)):
            cand = copy.copy(input)
            for mutated in __generate_mutations(input[i], prg):
                cand[i] = mutated[1]
                yield (mutated[0], cand)

def __generate_mutations_bfs(input, prg):
    pass

def generate_mutations(input):
    """A generator that produces all possible mutations from the given input."""
    semantics.collect_information(input)
    s = semantics.node_count(input)
    widgets = [progressbar.Bar(), ' ', progressbar.Counter(), ' / ', str(s)]
    prg = progressbar.ProgressBar(maxval = s, widgets = widgets)
    prg.start()
    yield from __generate_mutations(input, prg)
