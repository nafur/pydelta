import collections
import copy
import logging
import progressbar
import queue
import sys
import tempfile
import threading

import checker
import mutator
import options
import parser

Candidate = collections.namedtuple('Candidate', ['priority', 'counter', 'simplification', 'exprs'])
"""Represents a simplification candidate.

:code:`priority` gives the priority of this simplification (smallest first).

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
        self.q = queue.PriorityQueue(maxsize = 100)
        self.stop_operation = False
        self.finished_generation = False
        self.result = None
        self.result_lock = threading.Lock()

    def __empty_queue(self):
        """Empty the queue."""
        while not self.q.empty():
            self.q.get()
            self.q.task_done()

    def producer(self, input, skip = 0):
        """Produces new mutated variants of the given input."""
        counter = 0
        for candidate in mutator.generate_mutations(input):
            counter += 1
            if skip > 0:
                skip -= 1
                continue
            self.q.put(Candidate(1/candidate[1], counter, candidate[0], copy.deepcopy(candidate[2])))
            if self.stop_operation:
                break
        self.finished_generation = True

    def consumer(self):
        """Takes candidates from the queue and checks whether their output matches the reference result."""
        while not self.stop_operation:
            try:
                candidate = self.q.get(timeout = 0.25)
                tmp = tempfile.NamedTemporaryFile('w', suffix = '.smt2')
                tmp.write(parser.render_smtlib(candidate.exprs))
                tmp.flush()
                res = checker.execute(options.args().cmd, tmp.name)
                if checker.matches_reference(res):
                    with self.result_lock:
                        if self.result == None:
                            self.stop_operation = True
                            self.result = candidate
                self.q.task_done()
            except queue.Empty:
                if self.finished_generation:
                    break
        self.__empty_queue()

    def simplify(self, input, skip = 0):
        """Starts one producer thread and multiple consumer thread and then waits for a valid simplification."""
        assert self.q.empty()
        self.stop_operation = False
        self.finished_generation = False
        self.result = None
        try:
            threads = [
                threading.Thread(target = self.producer, name = 'producer', args = (input, skip))
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
