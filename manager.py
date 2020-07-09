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

Candidate = collections.namedtuple('Candidate', ['counter', 'simplification', 'exprs'])

class Manager:
    def __init__(self):
        self.q = queue.Queue(maxsize = 20)
        self.stop_operation = False
        self.finished_generation = False
        self.result = None
        self.result_lock = threading.Lock()

    def producer(self, input, skip = 0):
        counter = 0
        for candidate in mutator.generate_mutations(input):
            counter += 1
            if skip > 0:
                skip -= 1
                continue
            self.q.put(Candidate(counter, candidate[0], copy.deepcopy(candidate[1])))
            if self.stop_operation:
                break
        self.finished_generation = True

    def consumer(self):
        while not self.stop_operation:
            try:
                candidate = self.q.get(timeout = 0.25)
                tmp = tempfile.NamedTemporaryFile('w', suffix = '.smt2')
                tmp.write(parser.render_smtlib(candidate.exprs))
                tmp.flush()
                res = checker.execute(options.args().cmd, tmp.name)
                if checker.matches_golden(res):
                    with self.result_lock:
                        if self.result == None:
                            self.stop_operation = True
                            self.result = candidate
                            while not self.q.empty():
                                self.q.get()
                                self.q.task_done()
                self.q.task_done()
            except queue.Empty:
                if self.finished_generation:
                    break

    def simplify(self, input, skip = 0):
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
        except KeyboardInterrupt:
            sys.stdout.write('\n')
            logging.warning('Stopping all computations.')
            self.stop_operation = True
            while not self.q.empty():
                self.q.get()
                self.q.task_done()
            raise
            
        sys.stdout.write('\n')
        return self.result
