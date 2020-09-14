import logging
import os
import pprint
import sys
import time

from pydelta import checker
from pydelta import options
from pydelta import manager
from pydelta import mutator
from pydelta import parser

def setup_logging():
    logging.basicConfig(format = '[pydelta %(levelname)s] %(message)s')
    if options.args().verbose:
        logging.getLogger().setLevel(level=logging.DEBUG)
    else:
        logging.getLogger().setLevel(level=logging.INFO)

def check_options():
    if options.args().max_threads != 1:
        # configure number of threads
        if options.args().max_threads <= 0:
            options.args().max_threads = os.cpu_count() + options.args().max_threads
        logging.info('Using up to %d threads.', options.args().max_threads)

    if options.args().dump_config:
        pprint.pprint(vars(options.args()))

    # check input file
    if not os.path.isfile(options.args().inputfile):
        raise Exception('Input file is not a regular file')

    if options.args().parse_only:
        # only parse and print
        exprs = parser.parse_smtlib(open(options.args().inputfile).read())
        pprint.pprint(exprs)
        sys.exit(0)

    # check executable
    if len(options.args().cmd) == 0:
        raise Exception('No executable was specified as command')
    if not os.path.isfile(options.args().cmd[0]):
        raise Exception('Command "{}" is not a regular file'.format(options.args().cmd[0]))
    if not os.access(options.args().cmd[0], os.X_OK):
        raise Exception('Command "{}" is not executable'.format(options.args().cmd[0]))

def do_reference_run():
    if not checker.compute_reference(options.args().cmd, options.args().inputfile):
        logging.error('Computing the reference output failed.')
        sys.exit(1)

def parse_input():
    return parser.parse_smtlib(open(options.args().inputfile).read())

def run_pydelta(original):
    mutator.collect_mutators(options.args())
    skip = options.args().skip
    simplifications = 0
    m = manager.Manager()
    while True:
        try:
            # do one simplification step
            start = time.time()
            simp = m.simplify(original, skip)
            duration = time.time() - start
        except KeyboardInterrupt:
            logging.warning('Aborting. See %s for results.', options.args().outputfile)
            break
        if simp is None:
            logging.info('No further simplification found')
            if skip > 0:
                skip = 0
                logging.info('Starting over')
            else:
                # terminate
                parser.write_smtlib_to_file(original, options.args().outputfile)
                logging.info('Final input (written to %s):\n%s', options.args().outputfile, parser.render_smtlib(original))
                break
        else:
            simplifications += 1
            # write current status to file and continue
            logging.info('#%d: %s (%.2fs)', simplifications, simp.simplification, duration)
            skip = simp.counter
            original = simp.exprs
            parser.write_smtlib_to_file(original, options.args().outputfile)

    logging.info('Performed %d checks and %d simplifications', checker.CHECKS, simplifications)
    if checker.TIMEOUTS > 0:
        logging.info('Overall, checking timed out %d times', checker.TIMEOUTS)
