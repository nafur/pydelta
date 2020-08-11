import copy
import progressbar

from . import mutators_arithmetic
from . import mutators_bitvectors
from . import mutators_boolean
from . import mutators_core
from . import mutators_smtlib
from . import mutators_strings
from . import semantics

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


def __generate_mutations(original, prg):
    """Generate mutations from the given original, updating the progress bar."""
    prg.update(prg.currval + 1)
    yield from __mutate_node(original)
    if isinstance(original, list):
        for i,o in enumerate(original):
            cand = copy.copy(original)
            for mutated in __generate_mutations(o, prg):
                cand[i] = mutated[1]
                yield (mutated[0], cand)

def __generate_mutations_bfs(original, prg):
    pass

def generate_mutations(original):
    """A generator that produces all possible mutations from the given original."""
    semantics.collect_information(original)
    s = semantics.node_count(original)
    widgets = [progressbar.Bar(), ' ', progressbar.Counter(), ' / ', str(s)]
    prg = progressbar.ProgressBar(maxval = s, widgets = widgets)
    prg.start()
    prg.update_interval = 1
    yield from __generate_mutations(original, prg)
