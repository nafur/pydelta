import collections
import copy
import logging
import queue
import sys
import tempfile
import threading

from . import checker
from . import mutator
from . import options
from . import parser
from . import semantics

Candidate = collections.namedtuple('Candidate', ['counter', 'simplification', 'exprs'])
"""Represents a simplification candidate.

:code:`counter` contains the number of the simplified node in the pre-order iteration of :meth:`semantics.iterate_nodes`.

:code:`exprs` contains the simplified input.

:code:`simplification` contains the name of the applied mutator.
"""

class Manager:
    """Manages the asynchronous generation and checking of mutated inputs.
    One thread runs the :meth:`producer` method that fills a :class:`queue.Queue`
    while as many threads as given by the :code:`--max-threads` options run and evaluate the candidates from the queue.
    The :meth:`simplify` methods starts all threads and terminates them as soon as one valid simplication has been found.
    """
    def __init__(self):
        self.q = queue.Queue(maxsize = 20)
        self.stop_operation = False
        self.finished_generation = False
        self.result = None
        self.result_lock = threading.Lock()

    def __empty_queue(self):
        """Empty the queue."""
        try:
            while not self.q.empty():
                self.q.get(timeout = 0.1)
                self.q.task_done()
        except queue.Empty:
            pass


    def producer(self, original, skip = 0):
        """Produces new mutated variants of the given input."""
        counter = 0
        original_size = semantics.node_count(original)
        for candidate in mutator.generate_mutations(original):
            counter += 1
            if skip > 0:
                skip -= 1
                continue
            if options.args().mode_aggressive:
                if semantics.node_count(candidate[1]) > original_size * (1 - options.args().aggressiveness):
                    continue
            if options.args().mode_reduction_only:
                if semantics.node_count(candidate[1]) >= original_size:
                    continue
            self.q.put(Candidate(counter, candidate[0], copy.deepcopy(candidate[1])))
            if self.stop_operation:
                break
        self.finished_generation = True

    def consumer(self):
        """Takes candidates from the queue and checks whether their output matches the reference result."""
        while not self.stop_operation:
            try:
                candidate = self.q.get(timeout = 0.25)
                self.q.task_done()
                try:
                    with tempfile.NamedTemporaryFile('w', suffix = '.smt2') as tmp:
                        tmp.write(parser.render_smtlib(candidate.exprs))
                        tmp.flush()
                        res = checker.execute(options.args().cmd, tmp.name)
                except FileNotFoundError:
                    logging.info('Removing the temporary file failed.')
                if checker.matches_reference(res):
                    with self.result_lock:
                        if self.result is None:
                            self.stop_operation = True
                            self.result = candidate
            except queue.Empty:
                if self.finished_generation:
                    break
        self.__empty_queue()

    def simplify(self, original, skip = 0):
        """Starts one producer thread and multiple consumer thread and then waits for a valid simplification."""
        assert self.q.empty()
        self.q = queue.Queue(maxsize = 20)
        self.stop_operation = False
        self.finished_generation = False
        self.result = None
        try:
            threads = [
                threading.Thread(target = self.producer, name = 'producer', args = (original, skip))
            ] + [
                threading.Thread(target = self.consumer, name = 'consumer-{}'.format(i + 1))
                for i in range(options.args().max_threads)
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.__empty_queue()
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            logging.warning('Stopping all computations.')
            self.stop_operation = True
            self.__empty_queue()
            raise

        sys.stdout.write('\n')
        return self.result
