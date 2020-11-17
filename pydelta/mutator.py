import copy
import progressbar

from . import mutator_options
from . import semantics

enabled_mutators = []

def collect_mutators(args):
    """Initializes the list of all active mutators."""
    global enabled_mutators
    enabled_mutators = mutator_options.collect_mutators(args)

def __mutate_node(linput, ginput):
    """Apply all active mutators to the given node.
    Returns a list of all possible mutations as tuples :code:`(name, local, global)`
    where :code:`local` is a modification of the current node and :code:`global` is
    a modification of the whole input and one of those is always :code:`None`."""
    res = []
    for m in enabled_mutators:
        if hasattr(m, 'filter') and not m.filter(linput):
            continue
        if hasattr(m, 'mutations'):
            res = res + list(map(lambda x: (str(m), x, None), m.mutations(linput)))
        if hasattr(m, 'global_mutations'):
            res = res + list(map(lambda x: (str(m), None, x), m.global_mutations(linput, ginput)))
    return res

def __generate_mutations(linput, ginput, prg):
    """Generate mutations from the given original, updating the progress bar."""
    prg.update(prg.currval + 1)
    yield from __mutate_node(linput, ginput)
    if isinstance(linput, list):
        for i, o in enumerate(linput):
            cand = copy.copy(linput)
            for mutated in __generate_mutations(o, ginput, prg):
                if mutated[1] is not None:
                    cand[i] = mutated[1]
                    yield (mutated[0], cand, mutated[2])
                if mutated[2] is not None:
                    yield mutated

def generate_mutations(original):
    """A generator that produces all possible mutations from the given original."""
    semantics.collect_information(original)
    s = semantics.node_count(original)
    widgets = [progressbar.Bar(), ' ', progressbar.Counter(), ' / ', str(s)]
    prg = progressbar.ProgressBar(maxval = s, widgets = widgets)
    prg.start()
    prg.update_interval = 1
    for mutated in __generate_mutations(original, original, prg):
        if mutated[1] is not None:
            yield (mutated[0], mutated[1])
        if mutated[2] is not None:
            yield (mutated[0], mutated[2])
