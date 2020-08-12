import argparse
import sys

from . import version
from . import mutator_options

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.HelpFormatter):
    """A custom formatter for printing the commandline help.
    It combines :code:`argparse.ArgumentDefaultsHelpFormatter` with the :code:`argparse.HelpFormatter`,
    slightly increases the width reserved for the options and removed defaults for the mutator options."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_help_position = 35)

def parse_options():
    """Configures the commandline parse and then parse the commandline options."""
    usage = "{} [<options>] <inputfile> <cmd> [<cmd options>]".format(sys.argv[0])

    argp = argparse.ArgumentParser(usage = usage, formatter_class = CustomFormatter)
    argp.add_argument('inputfile', help = 'input file (in SMT-LIB v2 format)')
    argp.add_argument('cmd', nargs = argparse.REMAINDER, help = 'the command (with optional arguments)')

    argp.add_argument('-v', '--verbose', action='store_true', help = 'be more verbose')
    argp.add_argument('--version', action = 'version', version = version.VERSION)
    argp.add_argument('--dump-config', action='store_true', help = 'dump configuration')

    argp_modes = argp.add_argument_group('special modes')
    mutator_options.collect_mutator_modes(argp_modes)

    argp_checking = argp.add_argument_group('checking arguments')
    argp_checking.add_argument('--parse-only', action = 'store_true', help = 'only parse the input file')
    argp_checking.add_argument('--run-unchecked', action = 'store_true', help = 'apply mutations without checking them')
    argp_checking.add_argument('--max-threads', type = int, metavar = 'n', default = '-2',
                               help = 'number of threads to use; #processors+n if n<=0')
    argp_checking.add_argument('--timeout', type = int, metavar = 'seconds', default = 0, help = 'timeout for individual checks')
    argp_checking.add_argument('--memout', type = int, metavar = 'megabytes', default = 0, help = 'memout for individual checks')
    argp_checking.add_argument('--skip', type = int, metavar = 'n', default = 0, help = 'initially skip n candidates')

    argp_output = argp.add_argument_group('output arguments')
    argp_output.add_argument('--outputfile', metavar = 'filename', default = 'delta.out.smt2', help = 'filename for the output file')
    argp_output.add_argument('--pretty-print', action = 'store_true', help = 'pretty-print to output file')
    argp_output.add_argument('--wrap-lines', action = 'store_true', help = 'wrap lines in output file')

    argp_comparator = argp.add_argument_group('comparator arguments')
    argp_comparator.add_argument('--ignore-exitcode', action = 'store_true', help = 'ignore exitcode when comparing results')
    argp_comparator.add_argument('--ignore-output', action = 'store_true', help = 'ignore stdout and stderr when comparing results')
    argp_comparator.add_argument('--match-out', metavar = 'regex', help = 'regex that should match stdout')
    argp_comparator.add_argument('--match-err', metavar = 'regex', help = 'regex that should match stderr')

    mutator_options.collect_mutator_options(argp)

    return argp.parse_args()

__PARSED_ARGS = None

def args():
    """Returns the commandline options. Calls :code:`parse_options()` if parsing has not yet happened."""
    global __PARSED_ARGS
    if __PARSED_ARGS is None:
        __PARSED_ARGS = parse_options()
    return __PARSED_ARGS

def add_mutator_argument(argparser, name, default, help_msg):
    dest = 'mutator_{}'.format(name.replace('-', '_'))
    grp = argparser.add_mutually_exclusive_group()
    grp.add_argument('--{}'.format(name), action = 'store_true', default = default,
                     dest = dest, help = help_msg if not default else argparse.SUPPRESS)
    grp.add_argument('--no-{}'.format(name), action = 'store_false', default = default,
                     dest = dest, help = help_msg if default else argparse.SUPPRESS)
