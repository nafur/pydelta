import argparse
import sys

import mutator

__project_name__ = 'pyDelta'
__version__ = "0.1"
__author__  = "Gereon Kremer <gereon.kremer@gmail.com>"

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.HelpFormatter):
    """A custom formatter for printing the commandline help. It combines :code:`argparse.ArgumentDefaultsHelpFormatter` with the :code:`argparse.HelpFormatter`, slightly increases the width reserved for the options and removed defaults for the mutator options."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_help_position = 35)
    def _get_help_string(self, action):
        if action.dest.startswith('mutator_'):
            return action.help
        return super()._get_help_string(action)

def parse_options():
    """Configures the commandline parse and then parse the commandline options."""
    usage = "{} [<options>] <inputfile> <cmd> [<cmd options>]".format(sys.argv[0])

    argp = argparse.ArgumentParser(usage = usage, formatter_class = CustomFormatter)
    argp.add_argument('inputfile', help = 'input file (in SMT-LIB v2 format)')
    argp.add_argument('cmd', nargs = argparse.REMAINDER, help = 'the command (with optional arguments)')

    argp.add_argument('-v', '--verbose', action='store_true', help = 'be more verbose')
    argp.add_argument('--version', action = 'version', version = __version__)

    argp_checking = argp.add_argument_group('checking arguments')
    argp_checking.add_argument('--parse-only', action = 'store_true', help = 'only parse the input file')
    argp_checking.add_argument('--max-threads', type = int, metavar = 'n', default = '-1', help = 'number of threads to use; #processors+n if n<=0')
    argp_checking.add_argument('--timeout', type = int, metavar = 'seconds', default = 0, help = 'timeout for individual checks')
    argp_checking.add_argument('--memout', type = int, metavar = 'megabytes', default = 0, help = 'memout for individual checks')

    argp_output = argp.add_argument_group('output arguments')
    argp_output.add_argument('--outputfile', metavar = 'filename', default = 'delta.out.smt2', help = 'filename for the output file')
    argp_output.add_argument('--pretty-print', action = 'store_true', help = 'pretty-print to output file')
    argp_output.add_argument('--wrap-lines', action = 'store_true', help = 'wrap lines in output file')

    argp_comparator = argp.add_argument_group('comparator arguments')
    argp_comparator.add_argument('--ignore-output', action = 'store_true', help = 'ignore stdout and stderr when comparing results')
    argp_comparator.add_argument('--match-out', metavar = 'regex', help = 'regex that should match stdout')
    argp_comparator.add_argument('--match-err', metavar = 'regex', help = 'regex that should match stderr')

    mutator.collect_mutator_options(argp)

    return argp.parse_args()

parsed_args = None

def args():
    """Returns the commandline options. Calls :code:`parse_options()` if parsing has not yet happened."""
    global parsed_args
    if parsed_args == None:
        parsed_args = parse_options()
    return parsed_args

def __add_mutator_argument(argparser, option, name, action, help):
    dest = 'mutator_{}'.format(name.replace('-', '_'))
    argparser.add_argument(option, dest = dest, action = action, help = help)
def enable_mutator_argument(argparser, name, help):
    """Add an option :code:`--with-{name}` for a mutator."""
    __add_mutator_argument(argparser, '--with-{}'.format(name), name, 'store_true', help)
def disable_mutator_argument(argparser, name, help):
    """Add an option :code:`--without-{name}` for a mutator."""
    __add_mutator_argument(argparser, '--without-{}'.format(name), name, 'store_false', help)
