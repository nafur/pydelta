import collections
import logging
import re
import subprocess
import time

import options

ExecResult = collections.namedtuple('ExecResult', ['exitcode', 'stdout', 'stderr', 'runtime'])

def execute(cmd, inputfile):
    try:
        start = time.time()
        timeout = None if options.args().timeout == 0 else options.args().timeout
        res = subprocess.run(cmd + [inputfile], capture_output = True, timeout = timeout)
        duration = time.time() - start
        return ExecResult(res.returncode, res.stdout.decode('utf8').strip(), res.stderr.decode('utf8').strip(), duration)
    except TimeoutError:
        return ExecResult(-1, '', '', 0)

def compute_golden(cmd, inputfile):
    global golden
    golden = execute(cmd, inputfile)
    logging.info('Reference result: exit code {} after {} seconds'.format(golden.exitcode, golden.runtime))
    if options.args().ignore_output:
        logging.info('Reference output is being ignored')
    else:
        logging.info('Reference stdout: \"{}\"'.format(golden.stdout))
        logging.info('Reference stderr: \"{}\"'.format(golden.stderr))
        if options.args().match_out is not None:
            if not re.search(options.args().match_out, golden.stdout):
                logging.error('The pattern for stdout does not match the reference output')
                return False
        if options.args().match_err is not None:
            if not re.search(options.args().match_err, golden.stderr):
                logging.error('The pattern for stderr does not match the reference output')
                return False
    if options.args().timeout == 0:
        options.args().timeout = max(int(golden.runtime + 1) * 2, 1)
        logging.info('Using automatic timeout of {} seconds (reference run took {:.2f} seconds)'.format(options.args().timeout, golden.runtime))
    return True

def matches_golden(result):
    if golden.exitcode != result.exitcode:
        return False
    if not options.args().ignore_output:
        if options.args().match_out is None:
            if golden.stdout != result.stdout:
                return False
        else:
            if not re.search(options.args().match_out, golden.stdout):
                return False
        if options.args().match_err is None:
            if golden.stderr != result.stderr:
                return False
        else:
            if not re.search(options.args().match_err, golden.stderr):
                return False
    return True
