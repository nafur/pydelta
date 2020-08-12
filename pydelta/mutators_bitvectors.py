from . import options
from .semantics import *

NAME = 'bitvector'
MUTATORS = ['bv-constants', 'bv-eval-extract', 'bv-ite-to-bvcomp', 'bv-zero-concat']

def get_bitvector_constant_value(node):
    assert is_bitvector_constant(node)
    if is_leaf(node):
        if node.startswith('#b'):
            return (int(node[2:], 2), len(node[2:]))
        if node.startswith('#x'):
            return (int(node[2:], 16), len(node[2:]) * 4)
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
    for bvtype in get_variable_info().values():
        for wid in possible_bitvector_widths_imp(bvtype):
            widths.add(wid)
    return list(widths)

class PassBVConcatToZeroExtend:
    """Replace a concat with zero by zero_extend."""
    def filter(self, node):
        if not has_name(node) or get_name(node) != 'concat':
            return False
        if not is_bitvector_constant(node[1]):
            return False
        return get_bitvector_constant_value(node[1])[0] == 0
    def mutations(self, node):
        return [
            [['_', 'zero_extend', get_bitvector_constant_value(node[1])[1]], node[2]]
        ]
    def __str__(self):
        return 'replace concat by zero_extend'

class PassBVExtractConstants:
    """Evaluates a bitvector :code:`extract` if it is applied to a constant."""
    def filter(self, node):
        return is_bitvector_extract(node) and is_bitvector_constant(node[1])
    def mutations(self, node):
        upper = int(node[0][2])
        lower = int(node[0][3])
        constant = get_bitvector_constant_value(node[1])[0]
        constant = constant % (2**(upper + 1))
        constant -= constant % (2**lower)
        return [['_', 'bv{}'.format(constant), str(upper - lower + 1)]]
    def __str__(self):
        return 'evaluate bitvector extract on constant'

class PassBVOneZeroITE:
    """Replace an ite with bv1/bv0 cases by bvcomp."""
    def filter(self, node):
        if not is_ite(node):
            return False
        if not has_name(node[1]) or get_name(node[1]) != '=' or len(node[1]) != 3:
            return False
        if not is_bitvector_constant(node[2]) or get_bitvector_constant_value(node[2]) != (1, '1'):
            return False
        if not is_bitvector_constant(node[3]) or get_bitvector_constant_value(node[3]) != (0, '1'):
            return False
        return True
    def mutations(self, node):
        return [['bvcomp', node[1][1], node[1][2]]]
    def __str__(self):
        return 'eliminate ite with bv1 / bv0 cases'

class PassBVSimplifyConstant:
    """Replace a constant by a simpler version (smaller fewer bits)."""
    def filter(self, node):
        return is_bitvector_constant(node) and get_bitvector_constant_value(node)[0] not in [0, 1]
    def mutations(self, node):
        val, width = get_bitvector_constant_value(node)
        return ['#b{{:0>{}b}}'.format(width).format(v) for v in [val // 2, val // 10]]
    def __str__(self):
        return 'simplify bitvector constant'

def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'bitvector mutators')
    options.add_mutator_argument(argparser, 'bv-constants', True, 'replaces constants by simpler ones')
    options.add_mutator_argument(argparser, 'bv-eval-extract', True, 'evaluate bitvector extract on constants')
    options.add_mutator_argument(argparser, 'bv-ite-to-bvcomp', True, 'replaces bv1/bv0 ites by bvcomp')
    options.add_mutator_argument(argparser, 'bv-zero-concat', True, 'replaces concat with zero by zero_extend')

def collect_mutators(args):
    res = []
    if args.mutator_bitvector:
        if args.mutator_bv_constants:
            res.append(PassBVSimplifyConstant())
        if args.mutator_bv_eval_extract:
            res.append(PassBVExtractConstants())
        if args.mutator_bv_ite_to_bvcomp:
            res.append(PassBVOneZeroITE())
        if args.mutator_bv_zero_concat:
            res.append(PassBVConcatToZeroExtend())
    return res
