from mutators_generic import *
import options
from semantics import *

class PassArithmeticConstant(PassConstant):
    """Replaces a node by a constant. Only applies to nodes of arithmetic types. Is used with constants :code:`'0'` and :code:`'1'`."""
    def __init__(self, constant):
        super().__init__(lambda n: not is_arithmetic_constant(n) and is_arithmetic(n), constant)

def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'arithmetic', 'arithmetic mutators')
    options.disable_mutator_argument(argparser, 'constant-one', 'replace nodes by one')
    options.disable_mutator_argument(argparser, 'constant-zero', 'replace nodes by zero')

def collect_mutators(args):
    res = []
    if args.mutator_arithmetic:
        if args.mutator_constant_one:
            res.append(PassArithmeticConstant('1'))
        if args.mutator_constant_zero:
            res.append(PassArithmeticConstant('0'))
    return res
