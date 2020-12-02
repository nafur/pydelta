import logging
import re
import sys
import textwrap

from . import options

def lexer(text):
    __tokens = [
        ('COMMENT', ';[^\n]*'),
        ('LPAREN', '\\('),
        ('RPAREN', '\\)'),
        ('STRINGLIT', '"[^"]*"'),
        ('QUOTEDSYM', '\\|[^\\|]*\\|'),
        ('SYMBOL', '[:a-zA-Z0-9~!@$#%\\^&*_+=<>.?/-]+'),
        ('SPACE', '\\s+'),
        ('MISMATCH', '.'),
    ]
    __token_re = re.compile('|'.join(['(?P<{}>{})'.format(tok[0], tok[1]) for tok in __tokens]))

    for m in __token_re.finditer(text):
        kind = m.lastgroup
        if kind in ['SPACE', 'COMMENT']:
            continue
        if kind == 'MISMATCH':
            logging.warning('Unexpected  {}'.format(m.group()))
        yield m.group()

def parse_expression(tokens):
    """Parses a single S-sxpression from a token stream. Uses a simple iterative variant of a recursive descent parser with only a single parsing rule."""
    stack = []
    while True:
        tok = next(tokens)
        if tok == '(':
            stack.append([])
        elif tok == ')':
            cur = stack.pop()
            if not stack:
                return cur
            stack[-1].append(cur)
        else:
            stack[-1].append(tok)
    return None

def parse_smtlib(text):
    """Parses an SMT-LIB input to a sequence of nodes."""
    token_stream = lexer(text)
    exprs = []
    while True:
        try:
            exprs.append(parse_expression(token_stream))
        except StopIteration:
            break
        except RuntimeError as err:
            if isinstance(err.__cause__, StopIteration):
                break
            raise
    return exprs

def render_expression(expr):
    """Renders a node to a string."""
    if isinstance(expr, list):
        return '(' + ' '.join(map(render_expression, expr)) + ')'
    return expr

def render_pretty_expression(expr, indent = ''):
    """Renders a node to a string in a pretty way."""
    if isinstance(expr, list):
        if expr != [] and expr[0] in ['declare-const', 'declare-fun']:
            return render_expression(expr)
        if all(map(lambda e: not isinstance(e, list), expr)):
            return '(' + ' '.join(expr) + ')'
        res = '(' + render_pretty_expression(expr[0]) + '\n'
        for e in expr[1:]:
            res += indent + '\t' + render_pretty_expression(e, indent + '\t') + '\n'
        res += indent + ')'
        return res
    return expr

def render_smtlib(exprs):
    """Renders a sequence of nodes to a string."""
    if options.args().pretty_print:
        return '\n'.join(map(render_pretty_expression, exprs))
    res = map(render_expression, exprs)
    if options.args().wrap_lines:
        res = [line for r in res for line in textwrap.wrap(r, width = 78, subsequent_indent = '  ')]
    return '\n'.join(res)

def write_smtlib_to_file(exprs, filename):
    """Writes a sequence of nodes to a file."""
    open(filename, 'w').write(render_smtlib(exprs))
