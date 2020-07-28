import collections
import logging
import re
import resource
import subprocess
import time

import options

ExecResult = collections.namedtuple('ExecResult', ['exitcode', 'stdout', 'stderr', 'runtime'])
checks = 0

def limit_memory():
    if options.args().memout != 0:
        resource.setrlimit(resource.RLIMIT_AS, (options.args().memout * 1024 * 1024, resource.RLIM_INFINITY))

def execute(cmd, inputfile):
    """Executes :code:`cmd` on :code:`inputfile`."""
    try:
        global checks
        checks += 1
        start = time.time()
        timeout = None if options.args().timeout == 0 else options.args().timeout
        proc = subprocess.Popen(cmd + [inputfile], stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn = limit_memory)
        out,err = proc.communicate(timeout = timeout)
        duration = time.time() - start
        return ExecResult(proc.returncode, out.decode('utf8').strip(), err.decode('utf8').strip(), duration)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.wait(timeout = 2)
        except subprocess.TimeoutExpired:
            proc.kill()
        try:
            proc.wait(timeout = 2)
        except subprocess.TimeoutExpired:
            logging.warn('Killing pid {} failed. Please check manually to avoid memory exhaustion.')
        return ExecResult(-1, '', '', 0)

def compute_reference(cmd, inputfile):
    """Computes the reference result on the original input.
    Sets an automatic timeout if none was specified.
    """
    global reference
    reference = execute(cmd, inputfile)
    logging.info('Reference result: exit code {} after {} seconds'.format(reference.exitcode, reference.runtime))
    if options.args().ignore_output:
        logging.info('Reference output is being ignored')
    else:
        logging.info('Reference stdout: \"{}\"'.format(reference.stdout))
        logging.info('Reference stderr: \"{}\"'.format(reference.stderr))
        if options.args().match_out is not None:
            if not re.search(options.args().match_out, reference.stdout):
                logging.error('The pattern for stdout does not match the reference output')
                return False
        if options.args().match_err is not None:
            if not re.search(options.args().match_err, reference.stderr):
                logging.error('The pattern for stderr does not match the reference output')
                return False
    if options.args().timeout == 0:
        options.args().timeout = max(int(reference.runtime + 1) * 2, 1)
        logging.info('Using automatic timeout of {} seconds (reference run took {:.2f} seconds)'.format(options.args().timeout, reference.runtime))
    return True

def matches_reference(result):
    """Checkes whether the :code:`result` matches the reference result."""
    if reference.exitcode != result.exitcode:
        return False
    if not options.args().ignore_output:
        if options.args().match_out is None:
            if reference.stdout != result.stdout:
                return False
        else:
            if not re.search(options.args().match_out, reference.stdout):
                return False
        if options.args().match_err is None:
            if reference.stderr != result.stderr:
                return False
        else:
            if not re.search(options.args().match_err, reference.stderr):
                return False
    return True
