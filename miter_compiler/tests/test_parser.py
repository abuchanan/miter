import unittest
import types

from miter_compiler import parser
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
