from . import options
from .semantics import *

class PassStringSimplifyConstant:
    """Replace a string constant by a shorter version."""
    def filter(self, node):
        return is_string_constant(node) and node != '""'
    def mutations(self, node):
        content = node[1:-1]
        return ['"{}"'.format(c) for c in ['', content[1:], content[:-1]]]
    def __str__(self):
        return 'simplify string constant'

def collect_mutator_options(argparser):
    options.disable_mutator_argument(argparser, 'strings', 'strings mutators')
    options.disable_mutator_argument(argparser, 'str-constants', 'replaces constants by simpler ones')

def collect_mutators(args):
    res = []
    if args.mutator_strings:
        if args.mutator_str_constants:
            res.append(PassStringSimplifyConstant())
    return res