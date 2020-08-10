import collections
import copy
import logging
import queue
import sys
import tempfile
import threading

import checker
import mutator
import options
import parser

Candidate = collections.namedtuple('Candidate', ['counter', 'simplification', 'exprs'])
"""Represents a simplification candidate.

:code:`counter` contains the number of the simplified node in the pre-order iteration of :meth:`semantics.iterate_nodes`.

:code:`exprs` contains the simplified input.

:code:`simplification` contains the name of the applied mutator.
"""

class Manager:
    """Manages the asynchronous generation and checking of mutated inputs.
    One thread runs the :meth:`producer` method that fills a :class:`queue.Queue` while as many threads as given by the :code:`--max-threads` options run and evaluate the candidates from the queue.
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
        while not self.q.empty():
            self.q.get()
            self.q.task_done()

    def producer(self, original, skip = 0):
        """Produces new mutated variants of the given input."""
        counter = 0
        for candidate in mutator.generate_mutations(original):
            counter += 1
            if skip > 0:
                skip -= 1
                continue
            logging.debug('Put next candidate... current queue length: {}'.format(self.q.qsize()))
            self.q.put(Candidate(counter, candidate[0], copy.deepcopy(candidate[1])))
            if self.stop_operation:
                break
        self.finished_generation = True

    def consumer(self):
        """Takes candidates from the queue and checks whether their output matches the reference result."""
        while not self.stop_operation:
            try:
                candidate = self.q.get(timeout = 0.25)
                logging.debug('Testing next candidate in {}'.format(threading.current_thread().name))
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
                self.q.task_done()
            except queue.Empty:
                if self.finished_generation:
                    break
        logging.debug('Terminated {}'.format(threading.current_thread().name))
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
