from mutators_generic import *
import options
from semantics import *

class PassBoolConstant(PassConstant):
    """Replaces a node by a constant. Only applies to nodes of Boolean type. Is used with constants :code:`'true'` and :code:`'false'`."""
    def __init__(self, constant):
        super().__init__(lambda n: not is_boolean_constant(n) and is_boolean(n), constant)


def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'boolean', 'boolean mutators')
    options.disable_mutator_argument(argparser, 'constant-false', 'replace nodes by false')
    options.disable_mutator_argument(argparser, 'constant-true', 'replace nodes by true')
    

def collect_mutators(args):
    res = []
    if args.mutator_boolean:
        if args.mutator_constant_false:
            res.append(PassBoolConstant('false'))
        if args.mutator_constant_true:
            res.append(PassBoolConstant('true'))
    return res
