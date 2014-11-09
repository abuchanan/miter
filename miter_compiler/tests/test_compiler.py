import ast
import logging
import unittest
import types

from miter_compiler import compiler, lexer
from miter_compiler.lexer import Token


logging.basicConfig(level=logging.DEBUG)


def lex(s):
    return list(lexer.Lexer().lex(s))


class CompilerTests(unittest.TestCase):

    def assertAST(self, source, expected_dump):
        tokens = lex(source)
        tree = compiler.tokens_to_ast(tokens)
        dump = ast.dump(tree)
        self.assertEqual(dump, expected_dump)


class tokens_to_lines_Tests(unittest.TestCase):

    def test_all(self):
        tokens = [
            # Discards leading newlines
            Token('newline', ''),
            Token('newline', ''),
            Token('word', 'foo'),
            Token('word', 'bar'),
            Token('newline', ''),
            Token('word', 'foo'),
            Token('newline', ''),
            # Indent level is divided by indent_amount, given below
            Token('indent', 4),
            Token('word', 'baz'),

            # Empty lines are discarded
            Token('newline', ''),
            Token('indent', 4),

            # Try some trailing newlines, should be discarded
            Token('newline', ''),
            Token('newline', ''),
        ]
        lines = compiler.tokens_to_lines(tokens, indent_amount=4)

        self.assertIsInstance(lines, types.GeneratorType)

        lines = list(lines)

        self.assertEqual(len(lines), 3)

        self.assertEqual(lines[0].level, 0)
        self.assertEqual(lines[1].level, 0)
        self.assertEqual(lines[2].level, 1)

        self.assertEqual(lines[0].tokens, [
            Token('word', 'foo'),
            Token('word', 'bar'),
        ])

        self.assertEqual(lines[1].tokens, [
            Token('word', 'foo'),
        ])

        self.assertEqual(lines[2].tokens, [
            Token('word', 'baz'),
        ])


class StackTests(unittest.TestCase):

    def test_all(self):
        stack = compiler.Stack()
        self.assertEqual(stack.level, 0)
        self.assertEqual(stack.top, [])
        stack.top.append('foo')
        stack.save()
        self.assertEqual(stack.level, 1)
        self.assertEqual(stack.top, [])
        stack.restore()
        self.assertEqual(stack.level, 0)
        self.assertEqual(stack.top, ['foo'])


class lines_to_expressions_Tests(unittest.TestCase):

    def test_all(self):
        self.maxDiff = None
        Line = compiler.Line
        Expression = compiler.Expression

        lines = [
            Line(0, [Token('word', 'foo')]),

            Line(0, [Token('word', 'if')]),
            Line(1, [Token('word', 'if-block')]),
            Line(1, [Token('word', 'sub-if')]),
            Line(2, [Token('word', 'sub-if-block')]),
            Line(2, [Token('word', 'sub-if-block-2')]),

            Line(0, [Token('word', 'else')]),
            Line(1, [Token('word', 'sub-else')]),
            Line(2, [Token('word', 'sub-else-block')]),
            Line(1, [Token('word', 'other-else')]),
        ]

        expressions = compiler.lines_to_expressions(lines)

        self.assertEqual(expressions, [
            Expression(lines[0].tokens),

            Expression(lines[1].tokens, [
                Expression(lines[2].tokens),
                Expression(lines[3].tokens, [
                    Expression(lines[4].tokens),
                    Expression(lines[5].tokens),
                ]),
            ]),

            Expression(lines[6].tokens, [
                Expression(lines[7].tokens, [
                    Expression(lines[8].tokens),
                ]),
                Expression(lines[9].tokens),
            ])
        ])
