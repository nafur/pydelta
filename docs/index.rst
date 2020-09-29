.. pyDelta documentation master file, created by
   sphinx-quickstart on Thu Jul 23 08:41:32 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyDelta: delta debugging for SMT-LIB
====================================

pyDelta is a `delta debugger <https://en.wikipedia.org/wiki/Delta_debugging>`_ for `SMT-LIB <http://smtlib.cs.uiowa.edu/language.shtml>`_ files.
It is heavily inspired by other similar tools like `ddSMT <https://github.com/aniemetz/ddSMT>`_, `DeltaSMT <http://fmv.jku.at/deltasmt/>`_ or `delta <https://github.com/smtrat/smtrat/tree/master/src/delta>`_.
pyDelta is based on a few fundamental ideas:

- parse generic S-expressions. This is very robust against changes to SMT-LIB or solver specific extensions. It also allows for a small parser and simple node structure. Most semantic information that is required for simplification can be recovered cheaply.
- parallel execution. Running multiple checks in parallel allows for significant speedups when minimizing faulty inputs.
- easy to extend. It should be fairly easy to add new simplifications by implementing new :doc:`mutators <mutators>`.
- fixed-point iteration. Simplifications are applied until no simplificationss are possible anywhere. Rerunning pyDelta on a minimized input should not yield further improvements.
- flexible to use. The options should cover most use cases, including checking for the exit code or checking for specific patterns in the (regular or error) output.

.. toctree::
   :maxdepth: 2

   modes
   mutators
   semantics
   utils
