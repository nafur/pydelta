from . import options
from .semantics import *

NAME = 'smtlib'
MUTATORS = ['check-sat-assuming']

class PassCheckSatAssuming:
    """Replaces a :code:`check-sat-assuming` by a regular :code:`check-sat`."""
    def filter(self, node):
        return has_name(node) and get_name(node) == 'check-sat-assuming'
    def mutations(self, node):
        return [['check-sat']]
    def __str__(self):
        return 'substitute check-sat-assuming by check-sat'

def collect_mutator_options(argparser):
    options.add_mutator_argument(argparser, NAME, True, 'smtlib mutators')
    options.add_mutator_argument(argparser, 'check-sat-assuming', True, 'replace check-sat-assuming by check-sat')

def collect_mutators(args):
    res = []
    if args.mutator_smtlib:
        if args.mutator_check_sat_assuming:
            res.append(PassCheckSatAssuming())
    return res
