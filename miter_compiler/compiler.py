import ast
import itertools

from miter_compiler.lexer import Token
from miter_compiler import builtins


# TODO unneeded?
def tokens_to_expression_tree(tokens):

    stack = []
    current = []

    for token in tokens:
        if token.type == 'expression start':
            stack.append(current)
            current = []

        elif token.type == 'expression end':
            if len(stack) > 0:
                parent = stack.pop()
                parent.append(current)
                current = parent
            else:
                raise Exception('Unexpected end of expression')

        else:
            current.append(token)

    if len(stack) > 0:
        raise Expection('Incomplete expression')

    # TODO handle empty expression? ignore?

    return current


class UnrecognizedTokenType(Exception): pass


class Word(object):

    def __init__(self, value):
        self.value = value


class ID(object):

    def __init__(self, value):
        self.value = value

    @property
    def ast(self):
        return ast.Name(id=self.value, ctx=ast.Load())


class Number(object):

    def __init__(self, value):
        self.value = value

    @property
    def ast(self):
        return ast.Num(n=self.value)


# TODO find a good naming scheme with statement, expression, and possibly phrase
class Expression(object):

    def __init__(self, tokens):
        self.parts = self._build_parts(tokens)
        self.signature = self._build_signature()
        self.variables = self._build_variables()
        self.handler = builtins.signature_map[self.signature]

    def _build_parts(self, tokens):
        tokens = iter(tokens)
        parts = []

        for token in tokens:

            if token.type == 'word':
                part = Word(token.value)

            elif token.type == 'number':
                part = Number(token.value)

            elif token.type == 'ID':
                part = ID(token.value)

            elif token.type == 'expression start':
                part = Expression(tokens)

            elif token.type == 'expression end':
                break

            else:
                raise UnrecognizedTokenType()

            parts.append(part)

        return parts

    def _build_signature(self):
        # TODO take types into account
        sig = []

        for part in self.parts:
            if isinstance(part, Word):
                sig.append(part.value)
            else:
                sig.append('_')

        return ' '.join(sig)

    def _build_variables(self):
        return [p for p in self.parts if not isinstance(p, Word)]

    @property
    def ast(self):
        return self.handler(*self.variables)


def iter_lines(tokens):

    while True:
        # Drop leading newlines
        tokens = itertools.dropwhile(lambda t: t.type == 'newline', tokens)
        l = list(itertools.takewhile(lambda t: t.type != 'newline', tokens))
        if l:
            yield l
        else:
            raise StopIteration


def tokens_to_ast(tokens):
    body = []

    for line in iter_lines(tokens):
        expr = Expression(line)
        expr_ast = expr.ast

        if not isinstance(expr_ast, ast.stmt):
            expr_ast = ast.Expr(expr_ast)

        body.append(expr_ast)

    return ast.Module(body=body)
