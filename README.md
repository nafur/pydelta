[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/nafur/pydelta/main)](https://github.com/nafur/pydelta/actions)
[![Read the Docs](https://img.shields.io/readthedocs/pydelta)](https://pydelta.readthedocs.io/)
[![PyPI](https://img.shields.io/pypi/v/pydelta-smt)](https://pypi.org/project/pydelta-smt/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydelta-smt)
[![PyPI - License](https://img.shields.io/pypi/l/pydelta-smt)](https://github.com/nafur/pydelta/blob/master/LICENSE)

pyDelta: delta debugging for SMT-LIB
====================================

pyDelta is a [delta debugger](https://en.wikipedia.org/wiki/Delta_debugging) for [SMT-LIB](http://smtlib.cs.uiowa.edu/language.shtml) files.
It is heavily inspired by other similar tools like [ddSMT](https://github.com/aniemetz/ddSMT), [DeltaSMT](http://fmv.jku.at/deltasmt/) or [delta](https://github.com/smtrat/smtrat/tree/master/src/delta).
pyDelta is based on a few fundamental ideas:

- parse generic S-expressions. This is very robust against changes to SMT-LIB or solver specific extensions. It also allows for a small parser and simple node structure. Most semantic information that is required for simplification can be recovered cheaply.
- parallel execution. Running multiple checks in parallel allows for significant speedups when minimizing faulty inputs.
- easy to extend. It should be fairly easy to add new simplifications by implementing new mutators.
- fixed-point iteration. Simplifications are applied until no simplificationss are possible anywhere. Rerunning pyDelta on a minimized input should not yield further improvements.
- flexible to use. The options should cover most use cases, including checking for the exit code or checking for specific patterns in the (regular or error) output.

Please visit https://pydelta.readthedocs.io for more documentation.
