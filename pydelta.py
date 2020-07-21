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

args = options.args()

logging.basicConfig(format = '[pydelta %(levelname)s] %(message)s')
if args.verbose:
    logging.getLogger().setLevel(level=logging.DEBUG)
else:
    logging.getLogger().setLevel(level=logging.INFO)


if not os.path.isfile(args.inputfile):
    raise Exception('Input file is not a regular file')

if args.parse_only:
    exprs = parser.parse_smtlib(open(args.inputfile).read())
    pprint.pprint(exprs)
    sys.exit(0)

if len(args.cmd) == 0:
    raise Exception('No executable was specified as command')
if not os.path.isfile(args.cmd[0]):
    raise Exception('Command "{}" is not a regular file'.format(args.cmd[0]))
if not os.access(args.cmd[0], os.X_OK):
    raise Exception('Command "{}" is not executable'.format(args.cmd[0]))

if args.max_threads != 1:
    if args.max_threads <= 0:
        args.max_threads = os.cpu_count() + args.max_threads
    logging.info('Using up to {} threads.'.format(args.max_threads))

mutator.collect_mutators(args)

if not checker.compute_golden(args.cmd, args.inputfile):
    logging.error('Computing the reference output failed.')
    sys.exit(1)

exprs = parser.parse_smtlib(open(args.inputfile).read())

skip = 0
m = manager.Manager()
while True:
    try:
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
            logging.info('Final input (written to {}):\n{}'.format(args.outputfile, parser.render_smtlib(exprs)))
            break
    else:
        logging.info('Simplified: {}'.format(simp.simplification))
        skip = simp.counter
        exprs = simp.exprs
        parser.write_smtlib_to_file(exprs, args.outputfile)
