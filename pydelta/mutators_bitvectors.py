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

class BVConcatToZeroExtend:
    """Replace a :code:`concat` with zero by :code:`zero_extend`."""
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

class BVElimBVComp:
    """Replace bvcomp by a regular equality."""
    def filter(self, node):
        return has_name(node) and get_name(node) == '=' and is_bitvector_constant(node[1]) and has_name(node[2]) and get_name(node[2]) == 'bvcomp'
    def mutations(self, node):
        return [
            ['='] + node[2][1:],
            ['not', ['='] + node[2][1:]],
        ]
    def __str__(self):
        return 'eliminate bvcomp by equality'

class BVEvalExtend:
    """Evaluates a bitvector :code:`(sign|zero)_extend` if it is applied to a constant or another :code:`(sign|zero)_extend`."""
    def filter(self, node):
        return is_bitvector_extend(node)
    def mutations(self, node):
        if is_bitvector_constant(node[1]):
            (val,width) = get_bitvector_constant_value(node[1])
            return [['_', 'bv{}'.format(val), str(width + node[0][2])]]
        return []
    def __str__(self):
        return 'evaluate bitvector extend'
class BVExtractConstants:
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

class BVOneZeroITE:
    """Replace an :code:`ite` with :code:`bv1`/:code:`bv0` cases by :code:`bvcomp`."""
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

class BVSimplifyConstant:
    """Replace a constant by a simpler version (smaller value)."""
    def filter(self, node):
        return is_bitvector_constant(node) and get_bitvector_constant_value(node)[0] not in [0, 1]
    def mutations(self, node):
        val, width = get_bitvector_constant_value(node)
        return ['#b{{:0>{}b}}'.format(width).format(v) for v in [val // 2, val // 10]]
    def global_mutations(self, linput, ginput):
        return [ substitute_repr(ginput, {repr(linput): rep}) for rep in self.mutations(linput) ]
    def __str__(self):
        return 'simplify bitvector constant'

class BVTransformToBool:
    """Turn BV constructs into Boolean constructs."""
    def filter(self, node):
        return has_name(node) and get_name(node) == '=' and is_bitvector_constant(node[1])
    def mutations(self, node):
        repl = {
            'bvand': 'and', 'bvor': 'or'
        }
        if has_name(node[2]) and get_name(node[2]) in repl:
            return [ [repl[get_name(node[2])]] + [
                ['=', node[1], c] for c in node[2][1:]
            ]]
        return []
    def __str__(self):
        return 'transform bitvector to boolean'

def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'bitvector mutators')
    options.add_mutator_argument(argparser, 'bv-constants', True, 'replaces constants by simpler ones')
    options.add_mutator_argument(argparser, 'bv-elim-bvcomp', True, 'replace bvcomp by a regular equality')
    options.add_mutator_argument(argparser, 'bv-eval-extract', True, 'evaluate bitvector extract on constants')
    options.add_mutator_argument(argparser, 'bv-eval-extend', True, 'evaluate bitvector extend on constants')
    options.add_mutator_argument(argparser, 'bv-ite-to-bvcomp', True, 'replaces bv1/bv0 ites by bvcomp')
    options.add_mutator_argument(argparser, 'bv-to-bool', True, 'replace bvor/bvand by regular Boolean operators')
    options.add_mutator_argument(argparser, 'bv-zero-concat', True, 'replaces concat with zero by zero_extend')

def collect_mutators(args):
    res = []
    if args.mutator_bitvector:
        if args.mutator_bv_constants:
            res.append(BVSimplifyConstant())
        if args.mutator_bv_elim_bvcomp:
            res.append(BVElimBVComp())
        if args.mutator_bv_eval_extract:
            res.append(BVExtractConstants())
        if args.mutator_bv_eval_extend:
            res.append(BVEvalExtend())
        if args.mutator_bv_ite_to_bvcomp:
            res.append(BVOneZeroITE())
        if args.mutator_bv_to_bool:
            res.append(BVTransformToBool())
        if args.mutator_bv_zero_concat:
            res.append(BVConcatToZeroExtend())
    return res
