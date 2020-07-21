import argparse
import sys

import mutator

__version__ = "0.1"
__author__  = "Gereon Kremer <gereon.kremer@gmail.com>"

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_help_position = 35)
    def _get_help_string(self, action):
        if action.dest.startswith('mutator_'):
            return action.help
        return super()._get_help_string(action)

class OptionParser:
    def __init__(self):
        usage = "{} [<options>] <inputfile> <cmd> [<cmd options>]".format(sys.argv[0])

        self.argp = argparse.ArgumentParser(usage = usage, formatter_class = CustomFormatter)

        self.argp.add_argument('inputfile', help = 'input file (in SMT-LIB v2 format)')
        self.argp.add_argument('cmd', nargs = argparse.REMAINDER, help = 'the command (with optional arguments)')
        self.argp.add_argument('--timeout', type = int, metavar = 'seconds', default = 0, help = 'timeout for individual checks')
        self.argp.add_argument('--max-threads', type = int, metavar = 'n', default = '-1', help = 'number of threads to use; #processors+n if n<=0')

        self.argp.add_argument('--parse-only', action = 'store_true', help = 'only parse the input file')
        self.argp.add_argument('-v', '--verbose', action='store_true', help = 'be more verbose')
        self.argp.add_argument('--version', action = 'version', version = __version__)
        self.argp.add_argument('--outputfile', metavar = 'filename', default = 'delta.out.smt2', help = 'filename for the output file')
        self.argp.add_argument('--pretty-print', action = 'store_true', help = 'pretty-print to output file')

        self.argp_comparator = self.argp.add_argument_group('comparator arguments')
        self.argp_comparator.add_argument('--ignore-output', action = 'store_true', help = 'ignore stdout and stderr when comparing results')
        self.argp_comparator.add_argument('--match-out', metavar = 'regex', help = 'regex that should match stdout')
        self.argp_comparator.add_argument('--match-err', metavar = 'regex', help = 'regex that should match stderr')

        mutator.collect_mutator_options(self.argp)

    def parse_args(self):
        return self.argp.parse_args()

parsed_args = None

def args():
    global parsed_args
    if parsed_args == None:
        parsed_args = OptionParser().parse_args()
    return parsed_args

def add_mutator_argument(argparser, option, name, action, help):
    dest = 'mutator_{}'.format(name.replace('-', '_'))
    argparser.add_argument(option, dest = dest, action = action, help = help)
def enable_mutator_argument(argparser, name, help):
    add_mutator_argument(argparser, '--with-{}'.format(name), name, 'store_true', help)
def disable_mutator_argument(argparser, name, help):
    add_mutator_argument(argparser, '--without-{}'.format(name), name, 'store_false', help)
