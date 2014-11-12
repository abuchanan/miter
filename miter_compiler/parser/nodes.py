"""
Contains AST node type classes.
"""


def signature(nodes):
    # TODO take types into account
    sig = []

    for node in nodes:
        if isinstance(node, Word):
            sig.append(node.value)
        else:
            sig.append('_')

    return ' '.join(sig)


class Module(object):

    def __init__(self, name, expressions):
        self.name = name
        self.expressions = expressions


class SimpleNode(object):

    """
    Base class for nodes with a simple format; they have a value and a block.
    """

    def __init__(self, value, block=None):
        self.value = value

        if block is not None:
            self.block = block
        else:
            self.block = []

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    def __eq__(self, other):
        return self.value == other.value


class Word(SimpleNode): pass
class ID(SimpleNode): pass
class Number(SimpleNode): pass
class Define(SimpleNode): pass
class Return(SimpleNode): pass


# TODO find a good naming scheme with statement, expression, and possibly phrase
class Expression(object):

    def __init__(self, parts, block=None):
        self.signature = signature(parts)
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
