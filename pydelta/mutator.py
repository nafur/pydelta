import collections
import copy
import progressbar

from . import mutator_options
from . import semantics

Mutation = collections.namedtuple('Mutation', ['nodeid', 'name', 'localm', 'globalm'])

enabled_mutators = []

def collect_mutators(args):
    """Initializes the list of all active mutators."""
    global enabled_mutators
    enabled_mutators = mutator_options.collect_mutators(args)

class MutationGenerator:
    def __init__(self, skip):
        self.__node_count = 0
        self.__node_skip = skip

    def __mutate_node(self, linput, ginput):
        """Apply all active mutators to the given node.
        Returns a list of all possible mutations as tuples :code:`(name, local, global)`
        where :code:`local` is a modification of the current node and :code:`global` is
        a modification of the whole input and one of those is always :code:`None`."""
        res = []
        for m in enabled_mutators:
            try:
                if hasattr(m, 'filter') and not m.filter(linput):
                    continue
                if hasattr(m, 'mutations'):
                    res = res + list(map(lambda x: Mutation(self.__node_count, str(m), x, None), m.mutations(linput)))
                if hasattr(m, 'global_mutations'):
                    res = res + list(map(lambda x: Mutation(self.__node_count, "(global) " + str(m), None, x), m.global_mutations(linput, ginput)))
            except:
                pass
        return res

    def __generate_mutations(self, linput, ginput, prg):
        """Generate mutations from the given original, updating the progress bar."""
        prg.update(prg.currval + 1)
        if self.__node_count >= self.__node_skip:
            yield from self.__mutate_node(linput, ginput)
        self.__node_count += 1
        if isinstance(linput, list):
            for i, o in enumerate(linput):
                cand = copy.copy(linput)
                for mutated in self.__generate_mutations(o, ginput, prg):
                    if mutated.localm is not None:
                        cand[i] = mutated.localm
                        yield Mutation(mutated.nodeid, mutated.name, cand, mutated.globalm)
                    if mutated.globalm is not None:
                        yield mutated

    def generate_mutations(self, original):
        """A generator that produces all possible mutations from the given original."""
        semantics.collect_information(original)
        s = semantics.node_count(original)
        widgets = [progressbar.Bar(), ' ', progressbar.Counter(), ' / ', str(s)]
        prg = progressbar.ProgressBar(maxval = s, widgets = widgets)
        prg.start()
        prg.update_interval = 1
        for mutated in self.__generate_mutations(original, original, prg):
            if mutated.localm is not None:
                yield (mutated.nodeid, mutated.name, mutated.localm)
            if mutated.globalm is not None:
                yield (mutated.nodeid, mutated.name, mutated.globalm)
