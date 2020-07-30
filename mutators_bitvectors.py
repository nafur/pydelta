import options
from semantics import *

def get_bitvector_constant_value(node):
    assert is_bitvector_constant(node)
    if is_leaf(node):
        if node.startswith('#b'): return (int(node[2:], 2), len(node[2:]))
        if node.startswith('#x'): return (int(node[2:], 16), len(node[2:]) * 4)
        assert False
    return (int(node[1][2:]), node[2])

def possible_bitvector_widths_imp(definition):
    if is_bitvector_type(definition):
        return [definition[2]]
    if not is_leaf(definition):
        return [w for arg in definition for w in possible_bitvector_widths_imp(arg)]
    return []

def possible_bitvector_widths(node):
    if has_type(node):
        assert is_bitvector_type(get_type(node))
        return [get_type(node)[2]]
    widths = set()
    for t in get_variable_info().values():
        for w in possible_bitvector_widths_imp(t):
            widths.add(w)
    return list(widths)

class PassBVExtractConstants:
    """Evaluates a bitvector :code:`extract` if it is applied to a constant."""
    def filter(self, node):
        return is_bitvector_extract(node) and is_bitvector_constant(node[1])
    def mutations(self, node):
        upper = int(node[0][2])
        lower = int(node[0][3])
        constant = get_bitvector_constant_value(node[1])[0]
        constant = constant % (2**(upper+1))
        constant -= constant % (2**lower)
        return [['_', 'bv{}'.format(constant), str(upper - lower + 1)]]
    def __str__(self):
        return 'evaluate bitvector extract on constant'

class PassBVSimplifyConstant:
    """Replace a constant by a simpler version (smaller fewer bits)."""
    def filter(self, node):
        return is_bitvector_constant(node) and get_bitvector_constant_value(node)[0] not in [0, 1]
    def mutations(self, node):
        val,width = get_bitvector_constant_value(node)
        return ['#b{{:0>{}b}}'.format(width).format(v) for v in [val // 2, val // 10]]
    def __str__(self):
        return 'simplify bitvector constant'


def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'bitvector', 'bitvector mutators')
    options.disable_mutator_argument(argparser, 'bv-eval-extract', 'evaluate bitvector extract on constants')
    options.disable_mutator_argument(argparser, 'bv-simplify-constants', 'replaces constants by simpler ones')

def collect_mutators(args):
    res = []
    if args.mutator_bitvector:
        if args.mutator_bv_eval_extract:
            res.append(PassBVExtractConstants())
        if args.mutator_bv_simplify_constants:
            res.append(PassBVSimplifyConstant())
    return res