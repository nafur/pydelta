import options
from semantics import *

def is_bitvector_type(node):
    if is_leaf(node) or len(node) != 3: return False
    if not has_name(node) or get_name(node) != '_': return False
    return node[1] == 'BitVec'

def is_bitvector_extract(node):
    if is_leaf(node) or len(node) != 2:
        return False
    if has_name(node) or not has_name(node[0]):
        return False
    if get_name(node[0]) != '_':
        return False
    return len(node[0]) == 4 and node[0][1] == 'extract'

def is_bitvector(node):
    if has_type(node):
        return is_bitvector_type(get_type(node))
    if is_ite(node):
        return is_bitvector(node[1])
    if has_name(node):
        if is_bitvector_extract(node):
            return True
        return get_name(node) in [
            'bvnot', 'bvand', 'bvor',
            'bvneg', 'bvadd', 'bvmul', 'bvudiv', 'bvurem', 'bvshl', 'bvshr', 'bvult',
            'concat'
        ]

def is_bitvector_constant(node):
    if is_leaf(node) or len(node) != 3: return False
    if not has_name(node) or get_name(node) != '_': return False
    return node[1].startswith('bv')

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
    for t in get_type_info().values():
        for w in possible_bitvector_widths_imp(t):
            widths.add(w)
    return list(widths)

class PassBVConstants:
    def __init__(self, constant):
        self.__constant = 'bv{}'.format(constant)
    def filter(self, node):
        return not is_bitvector_constant(node) and is_bitvector(node)
    def mutations(self, node):
        return [['_', self.__constant, t] for t in possible_bitvector_widths(node)]
    def __str__(self):
        return 'substitute by bitvector constant \"{}\"'.format(self.__constant)

class PassBVExtractConstants:
    def filter(self, node):
        return is_bitvector_extract(node) and is_bitvector_constant(node[1])
    def mutations(self, node):
        upper = int(node[0][2])
        lower = int(node[0][3])
        constant = int(node[1][1][2:])
        constant = constant % (2**(upper+1))
        constant -= constant % (2**lower)
        return [['_', 'bv{}'.format(constant), str(upper - lower + 1)]]
    def __str__(self):
        return 'evaluate bitvector extract on constant'

def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'bitvector', 'bitvector mutators')
    options.disable_mutator_argument(argparser, 'bv-constant-one', 'replace bitvector nodes by one')
    options.disable_mutator_argument(argparser, 'bv-constant-zero', 'replace bitvector nodes by zero')
    options.disable_mutator_argument(argparser, 'bv-eval-extract', 'evaluate bitvector extract on constants')

def collect_mutators(args):
    res = []
    if args.mutator_bitvector:
        if args.mutator_bv_constant_one:
            res.append(PassBVConstants('1'))
        if args.mutator_bv_constant_zero:
            res.append(PassBVConstants('0'))
        if args.mutator_bv_eval_extract:
            res.append(PassBVExtractConstants())
    return res