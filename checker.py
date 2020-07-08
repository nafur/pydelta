import collections
import logging
import subprocess
import time

import options

ExecResult = collections.namedtuple('ExecResult', ['exitcode', 'stdout', 'stderr', 'runtime'])

def execute(cmd, inputfile, timeout = None):
    try:
        start = time.time()
        res = subprocess.run(cmd + [inputfile], capture_output = True, timeout = timeout)
        duration = time.time() - start
        return ExecResult(res.returncode, res.stdout.decode('utf8').strip(), res.stderr.decode('utf8').strip(), duration)
    except TimeoutError:
        return ExecResult(-1, '', '', 0)

def compute_golden(cmd, inputfile):
    global golden
    golden = execute(cmd, inputfile)
    logging.info('Reference result: exit code {} after {} seconds'.format(golden.exitcode, golden.runtime))
    logging.info('Reference stdout: \"{}\"'.format(golden.stdout))
    logging.info('Reference stderr: \"{}\"'.format(golden.stderr))

def matches_golden(result):
    if golden.exitcode != result.exitcode:
        return False
    if not options.args().ignore_output:
        if golden.stdout != result.stdout:
            return False
        if golden.stderr != result.stderr:
            return False
    return True
