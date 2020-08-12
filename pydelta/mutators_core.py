from . import options
from .semantics import *

NAME = 'core'
MUTATORS = [
    'constants', 'erase-children', 'inline-functions', 'let-elimination', 'let-substitution',
    'merge-children', 'replace-by-variable', 'sort-children', 'substitute-children'
]

class PassConstants:
    """Replaces any node by a constant."""
    def mutations(self, node):
        """Return :code:`get_constants(get_return_type(node))`."""
        res = get_constants(get_return_type(node))
        if node in res:
            return []
        return res
    def __str__(self):
        return 'substitute by a constant'

class PassEraseChildren:
    """Erases a single child of the given node."""
    def filter(self, node):
        return not is_leaf(node)
    def mutations(self, node):
        res = []
        for i in range(len(node)):
            tmp = node.copy()
            del tmp[i]
            res.append(tmp)
        return res
    def __str__(self):
        return 'erase child'

class PassInlineDefinedFuns:
    """Explicitly inlines a defined function."""
    def filter(self, node):
        return is_defined_function(node)
    def mutations(self, node):
        return [ get_defined_function(node)(node[1:]) ]
    def __str__(self):
        return 'inline defined functions'

class PassLetElimination:
    """Substitutes a let expression with its body."""
    def filter(self, node):
        return is_let(node)
    def mutations(self, node):
        return [node[2]]
    def __str__(self):
        return 'eliminate let binder'

class PassLetSubstitution:
    """Substitutes a variable bound by a let binder into the nested term."""
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

class PassMergeWithChildren:
    """Merges a node with one of its children. This is possible for n-ary operators like :code:`and` or :code:`+`."""
    def filter(self, node):
        return is_nary(node)
    def mutations(self, node):
        res = []
        for cid, child in enumerate(node):
            if has_name(child) and get_name(node) == get_name(child):
                res.append(node[:cid] + node[cid][1:] + node[cid + 1:])
        return res
    def __str__(self):
        return 'merge with child'

class PassReplaceByVariable:
    """Replaces a node by a variable."""
    def filter(self, node):
        return node_count(node) > 1
    def mutations(self, node):
        return [v for v in get_variable_info().keys() if node_count(v) < node_count(node)]
    def __str__(self):
        return 'substitute by existing variable'

class PassSortChildren:
    """Sorts the children of a node."""
    def filter(self, node):
        return not is_leaf(node)
    def mutations(self, node):
        s = sorted(node, key = node_count)
        if s != node:
            return [s]
        return []
    def __str__(self):
        return 'sort children'

class PassSubstituteChildren:
    """Substitutes a node with one of its children."""
    def filter(self, node):
        return not is_leaf(node) and not is_let(node)
    def mutations(self, node):
        return node[1:]
    def __str__(self):
        return 'substitute with child'

def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'core mutators')
    options.add_mutator_argument(argparser, 'constants', True, 'replace by theory constants')
    options.add_mutator_argument(argparser, 'erase-children', True, 'erase individual children of nodes')
    options.add_mutator_argument(argparser, 'inline-functions', True, 'inline defined functions')
    options.add_mutator_argument(argparser, 'let-elimination', True, 'eliminate let bindings')
    options.add_mutator_argument(argparser, 'let-substitution', True, 'substitute bound variables in let bindings')
    options.add_mutator_argument(argparser, 'merge-children', True, 'merge children into nodes')
    options.add_mutator_argument(argparser, 'replace-by-variable', True, 'replace with existing variable')
    options.add_mutator_argument(argparser, 'sort-children', True, 'sort children of nodes')
    options.add_mutator_argument(argparser, 'substitute-children', True, 'substitute nodes with their children')

def collect_mutators(args):
    res = []
    if args.mutator_core:
        if args.mutator_constants:
            res.append(PassConstants())
        if args.mutator_erase_children:
            res.append(PassEraseChildren())
        if args.mutator_inline_functions:
            res.append(PassInlineDefinedFuns())
        if args.mutator_let_elimination:
            res.append(PassLetElimination())
        if args.mutator_let_substitution:
            res.append(PassLetSubstitution())
        if args.mutator_merge_children:
            res.append(PassMergeWithChildren())
        if args.mutator_replace_by_variable:
            res.append(PassReplaceByVariable())
        if args.mutator_sort_children:
            res.append(PassSortChildren())
        if args.mutator_substitute_children:
            res.append(PassSubstituteChildren())
    return res
