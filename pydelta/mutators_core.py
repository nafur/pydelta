from . import options
from .semantics import *

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

class PassSubstituteChildren:
    """Substitutes a node with one of its children."""
    def filter(self, node):
        return not is_leaf(node)
    def mutations(self, node):
        return node[1:]
    def __str__(self):
        return 'substitute with child'

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

class PassMergeWithChildren:
    """Merges a node with one of its children. This is possible for n-ary operators like :code:`and` or :code:`+`."""
    def filter(self, node):
        return is_nary(node)
    def mutations(self, node):
        res = []
        for cid,child in enumerate(node):
            if has_name(child) and get_name(node) == get_name(child):
                res.append(node[:cid] + node[cid][1:] + node[cid+1:])
        return res
    def __str__(self):
        return 'merge with child'

class PassReplaceVariables:
    """Replaces a variable by another variable."""
    def filter(self, node):
        return get_return_type(node) is not None
    def mutations(self, node):
        return [ v for v in get_variables_with_type(get_return_type(node)) if is_smaller(v, node)]
    def __str__(self):
        return 'substitute by variable of same type'

class PassReplaceByVariable:
    """Replaces a node by a variable."""
    def filter(self, node):
        return node_count(node) > 1
    def mutations(self, node):
        return [v for v in get_variable_info().keys() if node_count(v) < node_count(node)]
    def __str__(self):
        return 'substitute by existing variable'

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

class PassInlineDefinedFuns:
    """Explicitly inlines a defined function."""
    def filter(self, node):
        return is_defined_function(node)
    def mutations(self, node):
        return [ get_defined_function(node)(node[1:]) ]
    def __str__(self):
        return 'inline defined functions'

def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'core', 'core mutators')
    options.disable_mutator_argument(argparser, 'constants', 'replace by theory constants')
    options.disable_mutator_argument(argparser, 'eliminate-lets', 'eliminate let bindings')
    options.disable_mutator_argument(argparser, 'erase-children', 'erase individual children of nodes')
    options.disable_mutator_argument(argparser, 'inline-functions', 'inline defined functions')
    options.disable_mutator_argument(argparser, 'merge-children', 'merge children into nodes')
    options.enable_mutator_argument(argparser, 'replace-by-variable', 'replace with existing variable')
    options.disable_mutator_argument(argparser, 'replace-variables', 'replace variables of same type')
    options.disable_mutator_argument(argparser, 'sort-children', 'sort children of nodes')
    options.disable_mutator_argument(argparser, 'substitute-children', 'substitute nodes with their children')

def collect_mutators(args):
    res = []
    if args.mutator_core:
        if args.mutator_eliminate_lets:
            res.append(PassLetSubstitution())
        if args.mutator_erase_children:
            res.append(PassEraseChildren())
        if args.mutator_inline_functions:
            res.append(PassInlineDefinedFuns())
        if args.mutator_constants:
            res.append(PassConstants())
        if args.mutator_merge_children:
            res.append(PassMergeWithChildren())
        if args.mutator_replace_by_variable:
            res.append(PassReplaceByVariable())
        if args.mutator_replace_variables:
            res.append(PassReplaceVariables())
        if args.mutator_sort_children:
            res.append(PassSortChildren())
        if args.mutator_substitute_children:
            res.append(PassSubstituteChildren())
    return res
