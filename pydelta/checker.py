import collections
import logging
import re
import resource
import subprocess
import time

from . import options

ExecResult = collections.namedtuple('ExecResult', ['exitcode', 'stdout', 'stderr', 'runtime'])
__REFERENCE = ExecResult(-1, '', '', -1)
CHECKS = 0
TIMEOUTS = 0

def limit_memory():
    """Apply memory limit given by :code:`--memout`."""
    if options.args().memout != 0:
        resource.setrlimit(resource.RLIMIT_AS, (options.args().memout * 1024 * 1024, resource.RLIM_INFINITY))

def execute(cmd, inputfile):
    """Executes :code:`cmd` on :code:`inputfile`."""
    try:
        global CHECKS
        CHECKS += 1
        if options.args().run_unchecked:
            return ExecResult(0, '', '', 0)
        start = time.time()
        timeout = None if options.args().timeout == 0 else options.args().timeout
        proc = subprocess.Popen(cmd + [inputfile], stdout = subprocess.PIPE, stderr = subprocess.PIPE, preexec_fn = limit_memory)
        out, err = proc.communicate(timeout = timeout)
        duration = time.time() - start
        return ExecResult(proc.returncode, out.decode('utf8').strip(), err.decode('utf8').strip(), duration)
    except subprocess.TimeoutExpired:
        global TIMEOUTS
        TIMEOUTS += 1
        proc.terminate()
        try:
            proc.wait(timeout = 2)
        except subprocess.TimeoutExpired:
            proc.kill()
        try:
            proc.wait(timeout = 2)
        except subprocess.TimeoutExpired:
            logging.warning('Killing pid %d failed. Please check manually to avoid memory exhaustion.', proc.pid)
        return ExecResult(-1, '', '', 0)

def compute_reference(cmd, inputfile):
    """Computes the reference result on the original input.
    Sets an automatic timeout if none was specified.
    """
    global __REFERENCE
    __REFERENCE = execute(cmd, inputfile)
    logging.info('Reference result: exit code %d after %.2f seconds', __REFERENCE.exitcode, __REFERENCE.runtime)
    if options.args().ignore_output:
        logging.info('Reference output is being ignored')
    else:
        logging.info('Reference stdout: \"%s\"', __REFERENCE.stdout)
        logging.info('Reference stderr: \"%s\"', __REFERENCE.stderr)
        if options.args().match_out is not None:
            if not re.search(options.args().match_out, __REFERENCE.stdout):
                logging.error('The pattern for stdout does not match the reference output')
                return False
        if options.args().match_err is not None:
            if not re.search(options.args().match_err, __REFERENCE.stderr):
                logging.error('The pattern for stderr does not match the reference output')
                return False
    if options.args().timeout == 0:
        options.args().timeout = max(int(__REFERENCE.runtime + 1) * 2, 1)
        logging.info('Using automatic timeout of %d seconds (reference run took %.2f seconds)', options.args().timeout, __REFERENCE.runtime)
    return True

def matches_reference(result):
    """Checkes whether the :code:`result` matches the reference result."""
    if options.args().run_unchecked:
        return True
    if not options.args().ignore_exitcode:
        if __REFERENCE.exitcode != result.exitcode:
            return False
    if not options.args().ignore_output:
        if options.args().match_err is None and options.args().match_out is None:
            # if neither --match-err or --match-out are given
            if __REFERENCE.stdout != result.stdout:
                return False
            if __REFERENCE.stderr != result.stderr:
                return False
        else:
            # --match-err or --match-out are given
            if options.args().match_err is not None:
                if not re.search(options.args().match_err, result.stderr):
                    return False
            if options.args().match_out is not None:
                if not re.search(options.args().match_out, result.stdout):
                    return False
    return True
