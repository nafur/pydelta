import logging
import re

defined_functions = {}
type_lookup = {}

##### Generic node utilities
def is_leaf(node):
    """Checks whether a node is a leaf node."""
    return not isinstance(node, list)
def is_empty(node):
    return node == []
def has_name(node):
    """Checks whether a node has a name, that is its first child is a leaf node."""
    return not is_leaf(node) and not is_empty(node) and is_leaf(node[0])
def get_name(node):
    """Gets the name of a node, asserting that has_name(node)."""
    assert has_name(node)
    return node[0]

def has_type(node):
    return is_leaf(node) and node in type_lookup
def get_type(node):
    assert has_type(node)
    return type_lookup[node]
def is_ite(node):
    return has_name(node) and get_name(node) == 'ite'
def is_defined_function(node):
    return has_name(node) and get_name(node) in defined_functions
def get_defined_function(node):
    assert is_defined_function(node)
    return defined_functions[get_name(node)]

##### Generic constructs
def is_let(node):
    return has_name(node) and get_name(node) == 'let'
def is_empty_let(node):
    return is_let(node) and is_empty(node[1])

##### Type information about nodes
def get_type_info():
    return type_lookup

def is_arithmetic(node):
    if has_type(node):
        return get_type(node) in ['Real', 'Int']
    if is_ite(node):
        return is_arithmetic(node[1])
    if has_name(node):
        return get_name(node) in ['*', '+', '-', '/', 'div', 'mod', 'abs']
    return False

def is_arithmetic_constant(node):
    return is_leaf(node) and re.match('[0-9]+(\\.[0-9]*)?', node) != None

def is_boolean(node):
    if has_type(node):
        return get_type(node) in ['Bool']
    if is_ite(node):
        return is_boolean(node[1])
    if has_name(node):
        return get_name(node) in [
            # Core theory
            'not', '=>', 'and', 'or', 'xor', '=', 'distinct'
            '<', '<=', '>', '>=', 
        ]
    return False
def is_boolean_constant(node):
    return is_leaf(node) and node in ['false', 'true']

def is_bitvector_type(node):
    if is_leaf(node) or len(node) != 3: return False
    if not has_name(node) or get_name(node) != '_': return False
    return node[1] == 'BitVec'

def is_bitvector(node):
    if has_type(node):
        return is_bitvector_type(get_type(node))
    if is_ite(node):
        return is_bitvector(node[1])
    if has_name(node):
        return get_name(node) in [
            # bv theory
            'bvnot', 'bvand', 'bvor',
            'bvneg', 'bvadd', 'bvmul', 'bvudiv', 'bvurem', 'bvshl', 'bvshr', 'bvult'
        ]

def is_bitvector_constant(node):
    if is_leaf(node) or len(node) != 3: return False
    if not has_name(node) or get_name(node) != '_': return False
    return node[1].startswith('bv')

def possible_bitvector_widths_imp(definition):
    if is_bitvector_type(definition):
        return [definition[2]]
    if not is_leaf(definition):
        return [w for arg in definition for w in possible_bitvector_widths_imp(arg)]
    return []

def possible_bitvector_widths(node):
    if has_type(node):
        assert is_bitvector_type(get_type(node))
        return [get_type(node)[2]]
    widths = set()
    for t in get_type_info().values():
        for w in possible_bitvector_widths_imp(t):
            widths.add(w)
    return list(widths)

def node_count(exprs):
    if not is_leaf(exprs):
        return 1 + sum(map(node_count, exprs))
    return 1

def iterate_nodes(expr):
    yield expr
    if not is_leaf(expr):
        for e in expr:
            yield from iterate_nodes(e)

def substitute(node, repl):
    if is_leaf(node):
        return repl.get(node, node)
    return list(map(lambda n: substitute(n, repl), node))

def collect_information(exprs):
    global defined_functions
    global type_lookup
    defined_functions = {}
    type_lookup = { 'true': 'Bool', 'false': 'Bool' }

    for node in iterate_nodes(exprs):
        if not has_name(node):
            continue
        if get_name(node) == 'declare-const':
            assert len(node) == 3
            assert is_leaf(node[1])
            assert is_leaf(node[2])
            type_lookup[node[1]] = node[2]
        if get_name(node) == 'declare-fun':
            assert len(node) == 4
            assert is_leaf(node[1])
            type_lookup[node[1]] = node[3]
        if get_name(node) == 'define-fun':
            assert len(node) == 5
            assert is_leaf(node[1])
            assert not is_leaf(node[2])
            assert is_leaf(node[3])
            defined_functions[node[1]] = lambda args, node=node: substitute(node[4], {
                node[2][i][0]: args[i] for i in range(len(args))
            })
