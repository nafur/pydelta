from mutators_generic import *
import options
from semantics import *

def is_arithmetic(node):
    """Checks whether the :code:`node` has an arithmetic type."""
    if has_type(node):
        return get_type(node) in ['Real', 'Int']
    if is_ite(node):
        return is_arithmetic(node[1])
    if has_name(node):
        return get_name(node) in ['*', '+', '-', '/', 'div', 'mod', 'abs']
    return False

def is_arithmetic_constant(node):
    """Checks whether the :code:`node` is an arithmetic constant."""
    return is_leaf(node) and re.match('[0-9]+(\\.[0-9]*)?', node) != None

class PassArithmeticConstant(PassConstant):
    """Replaces a node by a constant. Only applies to nodes of arithmetic types. Is used with constants :code:`'0'` and :code:`'1'`."""
    def __init__(self, constant):
        super().__init__(lambda n: not is_arithmetic_constant(n) and is_arithmetic(n), constant)

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
    options.disable_mutator_argument(argparser, 'constant-one', 'replace nodes by one')
    options.disable_mutator_argument(argparser, 'constant-zero', 'replace nodes by zero')
    options.disable_mutator_argument(argparser, 'simplify-constants', 'replaces constants by simpler ones')

def collect_mutators(args):
    res = []
    if args.mutator_arithmetic:
        if args.mutator_constant_one:
            res.append(PassArithmeticConstant('1'))
        if args.mutator_constant_zero:
            res.append(PassArithmeticConstant('0'))
        if args.mutator_simplify_constants:
            res.append(PassArithmeticSimplifyConstant())
    return res
