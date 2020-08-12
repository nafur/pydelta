import copy
import progressbar

from . import mutator_options
from . import semantics

enabled_mutators = []

def collect_mutators(args):
    """Initializes the list of all active mutators."""
    global enabled_mutators
    enabled_mutators = mutator_options.collect_mutators(args)

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
        for i, o in enumerate(original):
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
