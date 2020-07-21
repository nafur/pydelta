from mutators_generic import *
import options
from semantics import *

def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'arithmetic', 'arithmetic mutators')
    options.disable_mutator_argument(argparser, 'constant-one', 'replace nodes by one')
    options.disable_mutator_argument(argparser, 'constant-zero', 'replace nodes by zero')

def collect_mutators(args):
    res = []
    if args.mutator_arithmetic:
        if args.mutator_constant_one:
            res.append(PassConstant(lambda n: not is_arithmetic_constant(n) and is_arithmetic(n), '1'))
        if args.mutator_constant_zero:
            res.append(PassConstant(lambda n: not is_arithmetic_constant(n) and is_arithmetic(n), '0'))
    return res
