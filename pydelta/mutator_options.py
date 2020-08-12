import argparse

from . import mutators_arithmetic
from . import mutators_bitvectors
from . import mutators_boolean
from . import mutators_core
from . import mutators_smtlib
from . import mutators_strings

def disable(namespace, option):
    setattr(namespace, 'mutator_{}'.format(option.replace('-', '_')), False)
def disable_all(namespace, options):
    for o in options:
        disable(namespace, o)

class LetEliminationAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        disable(namespace, mutators_arithmetic.NAME)
        disable(namespace, mutators_bitvectors.NAME)
        disable(namespace, mutators_boolean.NAME)
        disable_all(namespace, mutators_core.MUTATORS)
        disable(namespace, mutators_smtlib.NAME)
        disable(namespace, mutators_strings.NAME)
        setattr(namespace, 'mutator_let_elimination', True)
        setattr(namespace, 'mutator_let_substitution', True)

def collect_mutator_modes(argparser):
    argparser.add_argument('--mode-let-elimination', nargs = 0, action = LetEliminationAction, help = 'only eliminate let binders')

def collect_mutator_options(argparser):
    """Adds all options related to mutators to the given argument parser."""
    mutators_core.collect_mutator_options(argparser.add_argument_group('core mutator arguments'))
    mutators_boolean.collect_mutator_options(argparser.add_argument_group('boolean mutator arguments'))
    mutators_arithmetic.collect_mutator_options(argparser.add_argument_group('arithmetic mutator arguments'))
    mutators_bitvectors.collect_mutator_options(argparser.add_argument_group('bitvector mutator arguments'))
    mutators_smtlib.collect_mutator_options(argparser.add_argument_group('smtlib mutator arguments'))
    mutators_strings.collect_mutator_options(argparser.add_argument_group('strings mutator arguments'))

def collect_mutators(args):
    """Initializes the list of all active mutators."""
    res = []
    res += mutators_core.collect_mutators(args)
    res += mutators_boolean.collect_mutators(args)
    res += mutators_arithmetic.collect_mutators(args)
    res += mutators_bitvectors.collect_mutators(args)
    res += mutators_smtlib.collect_mutators(args)
    res += mutators_strings.collect_mutators(args)
    return res
