import logging
import re

defined_functions = {}
defined_variables = {}

##### Generic node utilities
def is_leaf(node):
    """Checks whether the :code:`node` is a leaf node."""
    return not isinstance(node, list)
def is_empty(node):
    """Checks whether the :code:`node` is empty."""
    return node == []
def has_name(node):
    """Checks whether the :code:`node` has a name, that is its first child is a leaf node."""
    return not is_leaf(node) and not is_empty(node) and is_leaf(node[0])
def get_name(node):
    """Gets the name of the :code:`node`, asserting that :code:`has_name(node)`."""
    assert has_name(node)
    return node[0]

##### Generic constructs
def is_ite(node):
    """Checks whether :code:`node` is an if-then-else expression."""
    return has_name(node) and get_name(node) == 'ite'
def is_let(node):
    """Checks whether :code:`node` is a let binder."""
    return has_name(node) and get_name(node) == 'let'

def is_defined_function(node):
    """Checks whether :code:`node` is a defined function."""
    return has_name(node) and get_name(node) in defined_functions
def get_defined_function(node):
    """Returns the defined function :code:`node` as a function object. Assumes :code:`is_defined_functions(node)`."""
    assert is_defined_function(node)
    return defined_functions[get_name(node)]

def is_nary(node):
    """Checks whether the :code:`node` is a n-ary operator."""
    if is_leaf(node) or not has_name(node):
        return False
    return get_name(node) in [
        '=>', 'and', 'or', 'xor',
        'bvand', 'bvor', 'bvadd', 'bvmul'
    ]

def node_count(exprs):
    """Counts the number of nodes within :code:`exprs`."""
    if not is_leaf(exprs):
        return 1 + sum(map(node_count, exprs))
    return 1

def iterate_nodes(expr):
    """A generator that performs an pre-order iteration over all nodes."""
    yield expr
    if not is_leaf(expr):
        for e in expr:
            yield from iterate_nodes(e)

def contains(node, sub):
    """Checks whether :code:`node` contains the node :code:`sub`."""
    if node == sub:
        return True
    if is_leaf(node):
        return False
    return any(map(lambda n: contains(n, sub), node))

def substitute(node, repl):
    """Performs substitution recursively within :code:`node`. :code:`repl` specifies the substitutions as a dictionary."""
    if is_leaf(node):
        return repl.get(node, node)
    return list(map(lambda n: substitute(n, repl), node))

##### Type information about nodes
def get_variable_info():
    """Returns the type lookup table."""
    return defined_variables
def has_type(node):
    """Checks whether :code:`node` was defined to have a certain type. Mostly applies to variables."""
    return is_leaf(node) and node in defined_variables
def get_type(node):
    """Returns the type of :code:`node` if it was defined to have a certain type. Assumes :code:`has_type(node)`."""
    assert has_type(node)
    return defined_variables[node]

def get_variables_with_type(type):
    """Returns all variables with the type :code:`type`."""
    return [v for v in defined_variables if defined_variables[v] == type]

def collect_information(exprs):
    """Initialize global lookups: defined functions and types."""
    global defined_functions
    global defined_variables
    defined_functions = {}
    defined_variables = {}

    for node in iterate_nodes(exprs):
        if not has_name(node):
            continue
        if get_name(node) == 'declare-const':
            assert len(node) == 3
            assert is_leaf(node[1])
            assert is_leaf(node[2])
            defined_variables[node[1]] = node[2]
        if get_name(node) == 'declare-fun':
            assert len(node) == 4
            assert is_leaf(node[1])
            defined_variables[node[1]] = node[3]
        if get_name(node) == 'define-fun':
            assert len(node) == 5
            assert is_leaf(node[1])
            assert not is_leaf(node[2])
            assert is_leaf(node[3])
            defined_functions[node[1]] = lambda args, node=node: substitute(node[4], {
                node[2][i][0]: args[i] for i in range(len(args))
            })
