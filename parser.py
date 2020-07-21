import collections
import re

import options

Token = collections.namedtuple('Token', ['kind', 'value'])

def lexer(text):
    __tokens = {
        'LPAREN' : '\\(',
        'RPAREN' : '\\)',
        'STRINGLIT' : '"[^"]*"',
        'QUOTEDSYM' : '\\|[^\\|]*\\|',
        'SYMBOL' : '[:a-zA-Z0-9~!@$%\\^&*_+=<>.?/-]+',
        'SPACE': '\\s+',
        'MISMATCH': '.',
    }
    __token_re = re.compile('|'.join(['(?P<{}>{})'.format(tok, __tokens[tok]) for tok in __tokens]))

    skip_until_newline = False
    for m in __token_re.finditer(text):
        kind = m.lastgroup
        value = m.group()
        if kind == 'SPACE':
            if skip_until_newline and value == '\n':
                skip_until_newline = False
            continue
        if skip_until_newline:
            continue
        if kind == 'MISMATCH' and value == ';':
            skip_until_newline = True
            continue
        yield Token(kind, value)

class Peekable:
    def __init__(self, generator):
        self.__gen = generator
        self.__peek = None
        self.__empty = False
        try:
            self.__peek = next(self.__gen)
        except StopIteration:
            self.__empty = True
    
    def __iter__(self):
        return self
    def __next__(self):
        if self.__empty:
            raise StopIteration
        res = self.__peek
        try:
            self.__peek = next(self.__gen)
        except StopIteration:
            self.__peek = None
            self.__empty = True
        return res
    def empty(self):
        return self.__empty
    def peek(self):
        return self.__peek


def parse_expression(tokens):
    tok = next(tokens)
    if tok.kind == 'LPAREN':
        args = []
        while tokens.peek().kind != 'RPAREN':
            args.append(parse_expression(tokens))
        assert tokens.peek().kind == 'RPAREN'
        next(tokens)
        return args
    return tok.value

def parse_smtlib(text):
    token_stream = Peekable(lexer(text))
    exprs = []
    while not token_stream.empty():
        exprs.append(parse_expression(token_stream))
    return exprs

def render_expression(expr):
    if isinstance(expr, list):
        return '(' + ' '.join(map(render_expression, expr)) + ')'
    else:
        return expr

def render_pretty_expression(expr, indent = ''):
    if isinstance(expr, list):
        if expr != [] and expr[0] in ['declare-fun']:
            return render_expression(expr)
        if all(map(lambda e: not isinstance(e, list), expr)):
            return '(' + ' '.join(expr) + ')'
        res = '(' + render_pretty_expression(expr[0]) + '\n'
        for e in expr[1:]:
            res += indent + '\t' + render_pretty_expression(e, indent + '\t') + '\n'
        res += indent + ')'
        return res
    else:
        return expr

def render_smtlib(exprs):
    if options.args().pretty_print:
        return "\n".join(map(render_pretty_expression, exprs))
    else:
        return "\n".join(map(render_expression, exprs))

def write_smtlib_to_file(exprs, filename):
    open(filename, 'w').write(render_smtlib(exprs))
