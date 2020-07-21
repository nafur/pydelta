from mutators_generic import *
import options
from semantics import *


def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'boolean', 'boolean mutators')
    options.disable_mutator_argument(argparser, 'constant-false', 'replace nodes by false')
    options.disable_mutator_argument(argparser, 'constant-true', 'replace nodes by true')
    

def collect_mutators(args):
    res = []
    if args.mutator_boolean:
        if args.mutator_constant_false:
            res.append(PassConstant(lambda n: not is_boolean_constant(n) and is_boolean(n), 'false'))
        if args.mutator_constant_true:
            res.append(PassConstant(lambda n: not is_boolean_constant(n) and is_boolean(n), 'true'))
    return res
