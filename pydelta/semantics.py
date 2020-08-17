import re

__defined_functions = {}
__defined_variables = {}

def is_leaf(node):
    """Checks whether the :code:`node` is a leaf node."""
    return not isinstance(node, list)

def is_empty(node):
    """Checks whether the :code:`node` is empty."""
    return node == []

def has_name(node):
    """Checks whether the :code:`node` has a name,
    that is its first child is a leaf node."""
    return not is_leaf(node) and not is_empty(node) and is_leaf(node[0])

def get_name(node):
    """Gets the name of the :code:`node`,
    asserting that :code:`has_name(node)`."""
    assert has_name(node)
    return node[0]

def is_smaller(n, m):
    if isinstance(n, str):
        if isinstance(m, str):
            return n < m
        else:
            return True
    else:
        if isinstance(m, str):
            return False
        else:
            return n < m

def is_ite(node):
    """Checks whether :code:`node` is an if-then-else expression."""
    return has_name(node) and get_name(node) == 'ite'

def is_let(node):
    """Checks whether :code:`node` is a let binder."""
    return has_name(node) and get_name(node) == 'let'

def is_defined_function(node):
    """Checks whether :code:`node` is a defined function."""
    return has_name(node) and get_name(node) in __defined_functions

def get_defined_function(node):
    """Returns the defined function :code:`node` as a function object.
    Assumes :code:`is___defined_functions(node)`."""
    assert is_defined_function(node)
    return __defined_functions[get_name(node)]

def is_nary(node):
    """Checks whether the :code:`node` is a n-ary operator."""
    if is_leaf(node) or not has_name(node):
        return False
    return get_name(node) in [
        '=>', 'and', 'or', 'xor', '=', 'distinct',
        '+', '-', '*', 'div', '/',
        '<=', '<', '>=', '>',
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
    """Performs substitution recursively within :code:`node`.
    :code:`repl` specifies the substitutions as a dictionary."""
    if is_leaf(node):
        return repl.get(node, node)
    return list(map(lambda n: substitute(n, repl), node))

def is_not(node):
    """Checks whether :code:`node` is a negation."""
    return has_name(node) and get_name(node) == 'not'

def is_bitvector_type(node):
    if is_leaf(node) or len(node) != 3:
        return False
    if not has_name(node) or get_name(node) != '_':
        return False
    return node[1] == 'BitVec'

def is_set_type(node):
    if is_leaf(node) or len(node) != 2:
        return False
    if not has_name(node) or get_name(node) != 'Set':
        return False
    return True

def is_boolean_constant(node):
    """Checks whether the :code:`node` is a Boolean constant."""
    return is_leaf(node) and node in ['false', 'true']

def is_arithmetic_constant(node):
    """Checks whether the :code:`node` is an arithmetic constant."""
    return is_leaf(node) and re.match('[0-9]+(\\.[0-9]*)?', node) is not None

def is_int_constant(node):
    """Checks whether the :code:`node` is an int constant."""
    return is_leaf(node) and re.match('^[0-9]+$', node) is not None

def is_real_constant(node):
    """Checks whether the :code:`node` is a real constant."""
    return is_leaf(node) and re.match('^[0-9]+(\\.[0-9]*)?$', node) is not None

def is_string_constant(node):
    """Checks whether the :code:`node` is a string constant."""
    return is_leaf(node) and re.match('^\"[^\"]*\"$', node) is not None

def is_bitvector_constant(node):
    if is_leaf(node):
        if node.startswith('#b'):
            return True
        if node.startswith('#x'):
            return True
        return False
    if len(node) != 3:
        return False
    if not has_name(node) or get_name(node) != '_':
        return False
    return node[1].startswith('bv')

def is_indexed_op(node):
    if is_leaf(node) or len(node) < 2:
        return False
    if has_name(node) or not has_name(node[0]):
        return False
    if get_name(node[0]) != '_':
        return False
    return True

def get_indexed_op_name(node):
    assert not is_leaf(node) and not is_leaf(node[0]) and node[0][0] == '_'
    return node[0][1]

def is_bitvector_extend(node):
    if not is_indexed_op(node):
        return False
    return len(node[0]) == 3 and node[0][1] in ['zero_extend', 'sign_extend']

def is_bitvector_extract(node):
    if not is_indexed_op(node):
        return False
    return len(node[0]) == 4 and node[0][1] == 'extract'

def is_bitvector_repeat(node):
    if not is_indexed_op(node):
        return False
    return len(node[0]) == 3 and node[0][1] == 'repeat'

def is_bitvector_rotate(node):
    if not is_indexed_op(node):
        return False
    return len(node[0]) == 3 and node[0][1] in ['rotate_left', 'rotate_right']

def get_bitvector_width(node):
    if is_bitvector_constant(node):
        if is_leaf(node):
            if node.startswith('#b'):
                return len(node[2:])
            if node.startswith('#x'):
                return len(node[2:]) * 4
        return int(node[2])
    if has_type(node):
        assert is_bitvector_type(get_type(node))
        return get_type(node)[2]
    if has_name(node):
        if get_name(node) in [
                'bvnot', 'bvand', 'bvor',
                'bvneg', 'bvadd', 'bvmul', 'bvudiv', 'bvurem',
                'bvshl', 'bvshr',
                'bvnand', 'bvnor', 'bvxor', 'bvsub', 'bvsdiv',
                'bvsrem', 'bvsmod', 'bvashr'
        ]:
            return get_bitvector_width(node[1])
        if get_name(node) == 'concat':
            assert len(node) == 3
            return get_bitvector_width(node[1]) + get_bitvector_width(node[2])
        if get_name(node) == 'bvcomp':
            return 1
        if is_bitvector_extend(node):
            return int(node[0][2]) + get_bitvector_width(node[1])
        if is_bitvector_extract(node):
            return int(node[0][2]) - int(node[0][3]) + 1
        if is_bitvector_repeat(node):
            return int(node[0][2]) * get_bitvector_width(node[1])
        if is_bitvector_rotate(node):
            return get_bitvector_width(node[1])
    return -1

def get_constants(const_type):
    """Returns a list of constants for the given type."""
    if const_type == 'Bool':
        return ['false', 'true']
    if const_type == 'Int':
        return ['0', '1']
    if const_type == 'Real':
        return ['0.0', '1.0']
    if is_bitvector_type(const_type):
        return [['_', c, const_type[2]] for c in ['bv0', 'bv1']]
    if is_set_type(const_type):
        return [['as', 'emptyset', const_type]] + [
            ['singleton', c] for c in get_constants(const_type[1])
        ]
    return []

def get_return_type(node):
    """Tries to figure out the return type of the given node.
    Returns :code:`None` if it can not be inferred."""
    if has_type(node):
        return get_type(node)
    if is_boolean_constant(node):
        return 'Bool'
    if is_bitvector_constant(node):
        return ['_', 'BitVec', str(get_bitvector_width(node))]
    if is_int_constant(node):
        return 'Int'
    if is_real_constant(node):
        return 'Real'
    bvwidth = get_bitvector_width(node)
    if bvwidth != -1:
        return ['_', 'BitVec', str(bvwidth)]
    if has_name(node):
        if is_ite(node):
            return get_return_type(node[1])
        # stuff that returns Bool
        if get_name(node) in [
                # core theory
                'not', '=>', 'and', 'or', 'xor', '=', 'distinct',
                # bv theory
                'bvult',
                # fp theory
                'fp.leq', 'fp.lt', 'fp.geq', 'fp.gt', 'fp.eq',
                'fp.isNormal', 'fp.isSubnormal', 'fp.isZero',
                'fp.isInfinite', 'fp.isNaN',
                'fp.isNegative', 'fp.isPositive',
                # int / real theory
                '<=', '<', '>>', '>', 'is_int',
                # sets theory
                'member', 'subset',
                # string theory
                'str.<', 'str.in_re', 'str.<=',
                'str.prefixof', 'str.suffixof', 'str.contains',
                'str.is_digit',
        ]:
            return 'Bool'
        # int theory
        if get_name(node) == '_' and len(node) == 3 and node[1] == 'divisible':
            return 'Bool'
        # stuff that returns Int
        if get_name(node) in [
                'div', 'mod', 'abs', 'to_int',
                # string theory
                'str.len', 'str.indexof', 'str.to_code', 'str.to_int',
                # sets theory
                'card'
        ]:
            return 'Int'
        # stuff that returns Real
        if get_name(node) in ['/', 'to_real', 'fp.to_real']:
            return 'Real'
        if get_name(node) in ['+', '-', '*']:
            if any(map(lambda n: get_return_type(n) == 'Real', node[1:])):
                return 'Real'
            else:
                return 'Int'
    return None

def get_variable_info():
    """Returns the type lookup table."""
    return __defined_variables

def has_type(node):
    """Checks whether :code:`node` was defined to have a certain type.
    Mostly applies to variables."""
    return is_leaf(node) and node in __defined_variables

def get_type(node):
    """Returns the type of :code:`node` if it was defined to have a certain type.
    Assumes :code:`has_type(node)`."""
    assert has_type(node)
    return __defined_variables[node]

def get_variables_with_type(var_type):
    """Returns all variables with the type :code:`var_type`."""
    return [
        v for v in __defined_variables
        if __defined_variables[v] == var_type
    ]


def collect_information(exprs):
    """Initialize global lookups: defined functions and types."""
    global __defined_functions
    global __defined_variables
    __defined_functions = {}
    __defined_variables = {}

    for node in iterate_nodes(exprs):
        if not has_name(node):
            continue
        if get_name(node) == 'declare-const':
            assert len(node) == 3
            assert is_leaf(node[1])
            __defined_variables[node[1]] = node[2]
        if get_name(node) == 'declare-fun':
            if not len(node) == 4:
                continue
            assert is_leaf(node[1])
            __defined_variables[node[1]] = node[3]
        if get_name(node) == 'define-fun':
            if not len(node) == 5:
                continue
            assert is_leaf(node[1])
            assert not is_leaf(node[2])
            if not is_leaf(node[3]):
                continue
            __defined_functions[node[1]] = lambda args, node=node: substitute(
                node[4],
                {node[2][i][0]: args[i] for i in range(len(args))}
            )
