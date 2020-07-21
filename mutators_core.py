import options
from semantics import *

class PassEraseChildren:
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
    def filter(self, node):
        return not is_leaf(node)
    def mutations(self, node):
        return node
    def __str__(self):
        return 'substitute with child'

class PassSortChildren:
    def filter(self, node):
        return not is_leaf(node)
    def mutations(self, node):
        s = sorted(node, key = lambda n: node_count(n))
        if s != node:
            return [s]
        return []
    def __str__(self):
        return 'sort children'

class PassMergeWithChildren:
    def filter(self, node):
        return is_nary(node)
    def mutations(self, node):
        res = []
        for cid in range(len(node)):
            if has_name(node[cid]) and get_name(node) == get_name(node[cid]):
                res.append(node[:cid] + node[cid][1:] + node[cid+1:])
        return res
    def __str__(self):
        return 'merge with child'

class PassReplaceVariables:
    def filter(self, node):
        return has_type(node)
    def mutations(self, node):
        return [ v for v in get_variables_with_type(get_type(node)) if v < node]
    def __str__(self):
        return 'substitute by variable of same type'

class PassLetSubstitution:
    def filter(self, node):
        return is_let(node) and not is_empty_let(node)
    def mutations(self, node):
        res = []
        for var in node[1]:
            if contains(node[2], var[0]):
                subs = substitute(node[2], {var[0]: var[1]})
                res.append([node[0], node[1], subs])
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


def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'core', 'core mutators')
    options.disable_mutator_argument(argparser, 'eliminate-lets', 'eliminate let bindings')
    options.disable_mutator_argument(argparser, 'erase-children', 'erase individual children of nodes')
    options.disable_mutator_argument(argparser, 'inline-functions', 'inline defined functions')
    options.disable_mutator_argument(argparser, 'merge-children', 'merge children into nodes')
    options.disable_mutator_argument(argparser, 'replace-variables', 'replace variables of same type')
    options.disable_mutator_argument(argparser, 'sort-children', 'sort children of nodes')
    options.disable_mutator_argument(argparser, 'substitute-children', 'substitute nodes with their children')

def collect_mutators(args):
    res = []
    if args.mutator_core:
        if args.mutator_eliminate_lets:
            res.append(PassLetSubstitution())
            res.append(PassLetElimination())
        if args.mutator_erase_children:
            res.append(PassEraseChildren())
        if args.mutator_inline_functions:
            res.append(PassInlineDefinedFuns())
        if args.mutator_merge_children:
            res.append(PassMergeWithChildren())
        if args.mutator_replace_variables:
            res.append(PassReplaceVariables())
        if args.mutator_sort_children:
            res.append(PassSortChildren())
        if args.mutator_substitute_children:
            res.append(PassSubstituteChildren())
    return res
