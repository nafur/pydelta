import options
from semantics import *

def is_arithmetic(node):
    """Checks whether the :code:`node` has an arithmetic type."""
    return get_return_type(node) in ['Int', 'Real']

def is_int(node):
    """Checks whether the :code:`node` has an int type."""
    return get_return_type(node) in ['Int']
    if has_type(node):
        return get_type(node) in ['Int']
    if is_ite(node):
        return is_int(node[1])
    if has_name(node):
        if get_name(node) in ['div', 'mod', 'abs']:
            return True
        return get_name(node) in [
                '*', '+', '-'
            ] and all(map(is_int, node[1:]))
    return False

def is_real(node):
    """Checks whether the :code:`node` has a real type."""
    return get_return_type(node) in ['Real']
    if has_type(node):
        return get_type(node) in ['Real']
    if is_ite(node):
        return is_real(node[1])
    if has_name(node):
        return get_name(node) in ['*', '+', '-', '/'] and any(map(is_real, node[1:]))
    return False

class PassArithmeticSimplifyConstant:
    """Replace a constant by a simpler version (smaller or fewer decimal places)."""
    def filter(self, node):
        return is_arithmetic_constant(node) and float(node) not in [0, 1]
    def mutations(self, node):
        f = float(node)
        if int(f) == f:
            i = int(f)
            return [str(i // 2), str(i // 10)]
        else:
            return [str(int(f)), node[:-1]]
    def __str__(self):
        return 'simplify arithmetic constant'


def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'arithmetic', 'arithmetic mutators')
    options.disable_mutator_argument(argparser, 'simplify-constants', 'replaces constants by simpler ones')

def collect_mutators(args):
    res = []
    if args.mutator_arithmetic:
        if args.mutator_simplify_constants:
            res.append(PassArithmeticSimplifyConstant())
    return res
