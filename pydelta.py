#!/usr/bin/env python3

import logging
import os
import pprint
import sys

import checker
import options
import manager
import mutator
import parser

# parse command line arguments
args = options.args()

# setup logging
logging.basicConfig(format = '[pydelta %(levelname)s] %(message)s')
if args.verbose:
    logging.getLogger().setLevel(level=logging.DEBUG)
else:
    logging.getLogger().setLevel(level=logging.INFO)

# check input file
if not os.path.isfile(args.inputfile):
    raise Exception('Input file is not a regular file')

if args.parse_only:
    # only parse and print
    exprs = parser.parse_smtlib(open(args.inputfile).read())
    pprint.pprint(exprs)
    sys.exit(0)

# check executable
if len(args.cmd) == 0:
    raise Exception('No executable was specified as command')
if not os.path.isfile(args.cmd[0]):
    raise Exception('Command "{}" is not a regular file'.format(args.cmd[0]))
if not os.access(args.cmd[0], os.X_OK):
    raise Exception('Command "{}" is not executable'.format(args.cmd[0]))

if args.max_threads != 1:
    # configure number of threads
    if args.max_threads <= 0:
        args.max_threads = os.cpu_count() + args.max_threads
    logging.info('Using up to {} threads.'.format(args.max_threads))

# do the reference run
if not checker.compute_reference(args.cmd, args.inputfile):
    logging.error('Computing the reference output failed.')
    sys.exit(1)

# setup mutators
mutator.collect_mutators(args)

# parse the input
exprs = parser.parse_smtlib(open(args.inputfile).read())

# setup the manager
skip = 0
m = manager.Manager()
while True:
    try:
        # do one simplification step
        simp = m.simplify(exprs, skip)
    except KeyboardInterrupt:
        logging.warning('Aborting. See {} for results.'.format(args.outputfile))
        break
    if simp == None:
        logging.info('No further simplification found')
        if skip > 0:
            skip = 0
            logging.info('Starting over')
        else:
            # terminate
            parser.write_smtlib_to_file(exprs, args.outputfile)
            logging.info('Final input (written to {}):\n{}'.format(args.outputfile, parser.render_smtlib(exprs)))
            break
    else:
        # write current status to file and continue
        logging.info('Simplified: {}'.format(simp.simplification))
        skip = simp.counter
        exprs = simp.exprs
        parser.write_smtlib_to_file(exprs, args.outputfile)

logging.info('Performed {} checks'.format(checker.checks))
