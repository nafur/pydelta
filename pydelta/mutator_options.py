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
    for opt in options:
        disable(namespace, opt)

class LetEliminationAction(argparse.Action):
    """Mode that only checks for let eliminations."""
    def __call__(self, parser, namespace, values, option_string = None):
        setattr(namespace, 'mode_let_elimination', True)
        disable(namespace, mutators_arithmetic.NAME)
        disable(namespace, mutators_bitvectors.NAME)
        disable(namespace, mutators_boolean.NAME)
        disable_all(namespace, mutators_core.MUTATORS)
        disable(namespace, mutators_smtlib.NAME)
        disable(namespace, mutators_strings.NAME)
        setattr(namespace, 'mutator_let_elimination', True)
        setattr(namespace, 'mutator_let_substitution', True)

class ReductionOnlyAction(argparse.Action):
    """Mode that only checks mutations that reduce the number of nodes."""
    def __call__(self, parser, namespace, values, option_string = None):
        setattr(namespace, 'mode_reduction_only', True)
        setattr(namespace, 'mutator_sort_children', False)

class AgressiveAction(argparse.Action):
    """Mode that only checks aggressive mutations."""
    def __call__(self, parser, namespace, values, option_string = None):
        setattr(namespace, 'mode_aggressive', True)
        disable(namespace, mutators_arithmetic.NAME)
        disable(namespace, mutators_bitvectors.NAME)
        disable(namespace, mutators_boolean.NAME)
        disable_all(namespace, mutators_core.MUTATORS)
        disable(namespace, mutators_strings.NAME)
        setattr(namespace, 'mutator_constants', True)
        setattr(namespace, 'mutator_erase_children', True)
        setattr(namespace, 'mutator_inline_functions', True)
        setattr(namespace, 'mutator_replace_by_variable', True)
        setattr(namespace, 'mutator_substitute_children', True)

class BeautifyAction(argparse.Action):
    """Mode that enables mutations merely beautify the output."""
    def __call__(self, parser, namespace, values, option_string = None):
        setattr(namespace, 'mutator_variable_names', True)
        setattr(namespace, 'pretty_print', True)

def collect_mutator_modes(argparser):
    argparser.add_argument('--mode-let-elimination', default = False, nargs = 0, action = LetEliminationAction, help = 'only eliminate let binders')
    argparser.add_argument('--mode-aggressive', default = False, nargs = 0, action = AgressiveAction, help = 'agressively minimize')
    argparser.add_argument('--aggressiveness', metavar = 'perc', type = float, default = 0.01,
                           help = 'percentage of the input a mutators needs to remove')
    argparser.add_argument('--mode-reduction-only', default = False, nargs = 0, action = ReductionOnlyAction, help = 'only allow reducing mutations')
    argparser.add_argument('--mode-beautify', default = False, nargs = 0, action = BeautifyAction, help = 'enables beautification mutators')

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
