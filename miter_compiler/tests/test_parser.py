import unittest
import types

from miter_compiler import parser
from miter_compiler.parser.nodes import *
from miter_compiler.lexer import Token


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
        lines = parser.tokens_to_lines(tokens, indent_amount=4)

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


class lines_to_expressions_Tests(unittest.TestCase):

    def test_basic_expression_nesting(self):
        self.maxDiff = None
        Line = parser.Line

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

        expressions = parser.lines_to_expressions(lines)

        self.assertEqual(expressions, [
            Expression([Word('foo')]),

            Expression([Word('if')], [
                Expression([Word('if-block')]),
                Expression([Word('sub-if')], [
                    Expression([Word('sub-if-block')]),
                    Expression([Word('sub-if-block-2')]),
                ]),
            ]),

            Expression([Word('else')], [
                Expression([Word('sub-else')], [
                    Expression([Word('sub-else-block')]),
                ]),
                Expression([Word('other-else')]),
            ]),
        ])
