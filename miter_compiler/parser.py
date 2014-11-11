"""
The parser converts tokens to an abstract syntax tree (AST).
An AST represents the program and its structure: expressions,
variables, etc. and their relationships to eachother.
"""


class UnrecognizedTokenType(Exception): pass


class Module(object):

    def __init__(self, name, expressions):
        self.name = name
        self.expressions = expressions


class SimpleNode(object):

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '{}({})'.format(self.node_type, self.value)

    def __eq__(self, other):
        return self.value == other.value


class Word(SimpleNode): pass
class ID(SimpleNode): pass
class Number(SimpleNode): pass


# TODO find a good naming scheme with statement, expression, and possibly phrase
class Expression(object):

    def __init__(self, signature, parts, block=None):
        self.signature = signature
        self.parts = parts
        self.args = [p for p in parts if not isinstance(p, Word)]

        if block is not None:
            self.block = block
        else:
            self.block = []

    def __repr__(self):
        return 'Expression({}, {})'.format(self.signature, self.block)

    def __eq__(self, other):
        return self.parts == other.parts and self.block == other.block


class AssignmentExpression(Expression): pass
class AdditionExpression(Expression): pass


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


def signature(nodes):
    # TODO take types into account
    sig = []

    for node in nodes:
        if isinstance(node, Word):
            sig.append(node.value)
        else:
            sig.append('_')

    return ' '.join(sig)


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

    sig = signature(parts)

    if sig == '_ + _':
        return AdditionExpression(sig, parts)

    elif sig == 'let _ be _':
        # TODO verify args. first arg must be ID
        return AssignmentExpression(sig, parts)

    else:
        return Expression(sig, parts)


def lines_to_expressions(lines):
    stack = Stack()

    for line_number, line in enumerate(lines):

        if line.level > stack.level + 1:
            raise Exception('Unexpected indent level')

        elif line_number == 0 and line.level > 0:
            raise Exception('Unexpected indent level in first line')

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
