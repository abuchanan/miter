import ast

from miter_compiler.lexer import Token
from miter_compiler import builtins


class UnrecognizedTokenType(Exception): pass


class Word(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Word({})'.format(self.value)

    def __eq__(self, other):
        return self.value == other.value


class ID(object):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    @property
    def ast(self):
        return ast.Name(id=self.value, ctx=ast.Load())


class Number(object):

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    @property
    def ast(self):
        return ast.Num(n=self.value)


# TODO find a good naming scheme with statement, expression, and possibly phrase
class Expression(object):

    def __init__(self, tokens, block=None):
        self.tokens = list(tokens)
        self.parts = self._build_parts(tokens)
        self.signature = self._build_signature()
        self.variables = self._build_variables()

        if block is not None:
            self.block = block
        else:
            self.block = []


    def __repr__(self):
        return 'Expression({}, {})'.format(self.tokens, self.block)

    def __eq__(self, other):
        return self.parts == other.parts and self.block == other.block

    def _build_parts(self, tokens):
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
                raise UnrecognizedTokenType(token.type)

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
        # TODO not sure Expression should be converting itself to a python AST
        #      probably want a target-language-specific converter
        handler = builtins.signature_map[self.signature]
        return handler(*self.variables)


class Line(object):

    def __init__(self, level=0, tokens=None):
        self.level = level
        if tokens is None:
            self.tokens = []
        else:
            self.tokens = tokens

    def __repr__(self):
        return 'Line({}, {})'.format(self.level, self.tokens)


class Stack(object):

    def __init__(self, factory=list):
        self._factory = factory
        self._data = []
        self.save()

    @property
    def level(self):
        return len(self._data) - 1

    @property
    def top(self):
        return self._data[-1]

    def save(self):
        self._data.append(self._factory())

    def restore(self):
        if self.level == 0:
            raise Exception("Already at level 0")

        return self._data.pop()


def tokens_to_lines(tokens, indent_amount=4):
    line = Line()

    for token in tokens:
        if token.type == 'newline':
            if line.tokens:
                yield line
                line = Line()

        elif token.type == 'indent':
            # TODO throw exception when value isn't divisible by indent amount
            line.level = token.value / indent_amount

        else:
            line.tokens.append(token)

    if line.tokens:
        yield line


def lines_to_expressions(lines):
    stack = Stack()

    for line_number, line in enumerate(lines):

        if line.level > stack.level + 1:
            raise Exception('Unexpected indent level')

        elif line_number == 0 and line.level > 0:
            raise Exception('Unexpected indent level in first line')

        elif line.level == stack.level + 1:
            stack.save()
            expr = Expression(line.tokens)
            stack.top.append(expr)

        elif line.level < stack.level:

            for _ in range(stack.level - line.level):
                block = stack.restore()
                stack.top[-1].block = block

            expr = Expression(line.tokens)
            stack.top.append(expr)

        else:
            expr = Expression(line.tokens)
            stack.top.append(expr)


    if stack.level > 0:
        for _ in range(stack.level):
            block = stack.restore()
            stack.top[-1].block = block

    return stack.top


def tokens_to_ast(tokens):
    body = []

    lines = tokens_to_lines(tokens)
    expressions = lines_to_expressions(lines)

    for expr in expressions:
        expr_ast = expr.ast

        if not isinstance(expr_ast, ast.stmt):
            expr_ast = ast.Expr(expr_ast)

        body.append(expr_ast)

    return ast.Module(body=body)
