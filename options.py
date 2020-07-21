import argparse
import sys

import mutator

__version__ = "0.1"
__author__  = "Gereon Kremer <gereon.kremer@gmail.com>"

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_help_position = 35)

class OptionParser:
    def __init__(self):
        usage = "{} [<options>] <inputfile> <cmd> [<cmd options>]".format(sys.argv[0])

        self.argp = argparse.ArgumentParser(usage = usage, formatter_class = CustomFormatter)

        self.argp.add_argument('inputfile', help = 'input file (in SMT-LIB v2 format)')
        self.argp.add_argument('cmd', nargs = argparse.REMAINDER, help = 'the command (with optional arguments)')

        self.argp.add_argument('--parse-only', action = 'store_true', help = 'only parse the input file')
        self.argp.add_argument('-v', '--verbose', action='store_true', help = 'be more verbose')
        self.argp.add_argument('--version', action = 'version', version = __version__)
        self.argp.add_argument('--outputfile', default = 'delta.out.smt2', help = 'filename for the output file')
        self.argp.add_argument('--max-threads', type = int, metavar = 'n', default = '-1', help = 'number of threads to use; #processors+n if n<=0')

        self.argp_comparator = self.argp.add_argument_group('comparator arguments')
        self.argp_comparator.add_argument('--ignore-output', action = 'store_true', help = 'ignore stdout and stderr when comparing results')
        self.argp_comparator.add_argument('--match-out', help = 'regex that should match stdout')
        self.argp_comparator.add_argument('--match-err', help = 'regex that should match stderr')

        self.argp_mutators = self.argp.add_argument_group('mutator arguments')
        mutator.collect_mutator_options(self.argp_mutators)

    def parse_args(self):
        return self.argp.parse_args()

parsed_args = None

def args():
    global parsed_args
    if parsed_args == None:
        parsed_args = OptionParser().parse_args()
    return parsed_args
