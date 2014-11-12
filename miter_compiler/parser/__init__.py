"""
The parser converts tokens to an abstract syntax tree (AST).
An AST represents the program and its structure: expressions,
variables, etc. and their relationships to eachother.
"""

from miter_compiler.stack import Stack
from miter_compiler.parser.nodes import *


class UnrecognizedTokenType(Exception): pass


class Line(object):

    def __init__(self, level=0, tokens=None):
        self.level = level
        if tokens is None:
            self.tokens = []
        else:
            self.tokens = tokens

    def __repr__(self):
        return 'Line({}, {})'.format(self.level, self.tokens)


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


def tokens_to_expression(tokens):
    # Important because we call this function recursively and we want to pass
    # and iterator, not a list.
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
            part = tokens_to_expression(tokens)

        elif token.type == 'expression end':
            break

        else:
            raise UnrecognizedTokenType(token.type)

        parts.append(part)

    return parts_to_expression(parts)


def parts_to_expression(parts):
    sig = signature(parts)

    if sig == '_':
        return parts[0]

    elif sig == '_ + _':
        return AdditionExpression(parts)

    elif sig == '_ = _':
        # TODO verify args. first arg must be ID
        return AssignmentExpression(parts)

    elif parts[0].value == 'define:':
        # TODO define statements can't contain nested expressions, only IDs
        # TODO define may not occur in a nested expression
        return Define(parts_to_expression(parts[1:]))

    elif parts[0].value == 'return':
        return Return(parts_to_expression(parts[1:]))

    # TODO handle expression that is a value, e.g. "1"

    else:
        return Expression(parts)


def lines_to_expressions(lines):
    stack = Stack()

    for line_number, line in enumerate(lines):

        if line.level > stack.level + 1:
            raise Exception('Unexpected indent level')

        elif line_number == 0 and line.level > 0:
            raise Exception('Unexpected indent level in first line')

        # TODO some expressions shouldn't be allowed to have blocks
        #      e.g. numbers? function calls? maybe IDs?
        #      throw error for this? or just ignore it? warning?
        elif line.level == stack.level + 1:
            stack.save()
            expr = tokens_to_expression(line.tokens)
            stack.top.append(expr)

        elif line.level < stack.level:

            for _ in range(stack.level - line.level):
                block = stack.restore()
                stack.top[-1].block = block

            expr = tokens_to_expression(line.tokens)
            stack.top.append(expr)

        else:
            expr = tokens_to_expression(line.tokens)
            stack.top.append(expr)


    if stack.level > 0:
        for _ in range(stack.level):
            block = stack.restore()
            stack.top[-1].block = block

    return stack.top


def tokens_to_ast(tokens):
    lines = tokens_to_lines(tokens)
    expressions = lines_to_expressions(lines)
    return Module('test', expressions)
