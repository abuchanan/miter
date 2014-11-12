import logging
import unittest

from miter_compiler import lexer
from miter_compiler.lexer import Token


logging.basicConfig(level=logging.DEBUG)


def lex(s):
    return list(lexer.Lexer().lex(s))


class LexerTests(unittest.TestCase):

    def assertTokens(self, s, expected):
        self.assertEqual(lex(s), expected)

    def test_words(self):
        tokens = lex('one two')
        self.assertEqual(tokens, [
            Token('word', 'one'),
            Token('word', 'two'),
        ])

    def test_skip_leading_whitespace(self):
        self.assertTokens('   one two', [
            Token('word', 'one'),
            Token('word', 'two'),
        ])

    def test_skip_trailing_whitespace(self):
        self.assertTokens('one two   ', [
            Token('word', 'one'),
            Token('word', 'two'),
        ])

    def test_IDs(self):
        self.assertTokens("'one' 'two and three'", [
            Token('ID', 'one'),
            Token('ID', 'two and three'),
        ])

    def test_words_and_IDs(self):
        self.assertTokens("'one' and  'two and three' and four", [
            Token('ID', 'one'),
            Token('word', 'and'),
            Token('ID', 'two and three'),
            # TODO should these come as one token?
            Token('word', 'and'),
            Token('word', 'four'),
        ])

    def test_single_quote_in_word(self):
        with self.assertRaises(lexer.InvalidWord_SingleQuote):
            lex("word'")

        with self.assertRaises(lexer.InvalidWord_SingleQuote):
            lex("word'fo")

    def test_multiline(self):
        self.assertTokens("one\ntwo", [
            Token('word', 'one'),
            Token('newline', ''),
            Token('word', 'two'),
        ])

        self.assertTokens("'one'\n'two'", [
            Token('ID', 'one'),
            Token('newline', ''),
            Token('ID', 'two'),
        ])

    def test_empty_ID_error(self):
        with self.assertRaises(lexer.InvalidID_Empty):
            lex("word '' foo")

        with self.assertRaises(lexer.InvalidID_Empty):
            lex("''")

    # TODO this is more like "unexpected end of input"
    def test_incomplete_ID_error(self):
        with self.assertRaises(lexer.InvalidID_Incomplete):
            lex("'something")

    def test_newline_in_ID_error(self):
        with self.assertRaises(lexer.InvalidID_Newline):
            lex("'something\nfoo'")

        with self.assertRaises(lexer.InvalidID_Newline):
            lex("'something\n'")

        with self.assertRaises(lexer.InvalidID_Newline):
            lex("'\nsomething'")

    def test_leading_and_trailing_whitespace_in_ID_is_ignored(self):
        self.assertTokens("'  foo bar  '", [
            Token('ID', 'foo bar')
        ])

    def test_plus_sign_as_word(self):
        self.assertTokens('x + y', [
            Token('word', 'x'),
            Token('word', '+'),
            Token('word', 'y'),
        ])

    def test_minus_sign_as_word(self):
        self.assertTokens('x - y', [
            Token('word', 'x'),
            Token('word', '-'),
            Token('word', 'y'),
        ])

    def test_indent(self):
        self.assertTokens('x\n  y', [
            Token('word', 'x'),
            Token('newline', ''),
            Token('indent', 2),
            Token('word', 'y'),
        ])

    def test_simple_nested_expression(self):
        self.assertTokens('if (not one)', [
            Token('word', 'if'),
            Token('expression start'),
            Token('word', 'not'),
            Token('word', 'one'),
            Token('expression end')
        ])

    def test_expression_after_ID(self):
        self.assertTokens("(not 'one')", [
            Token('expression start'),
            Token('word', 'not'),
            Token('ID', 'one'),
            Token('expression end')
        ])

    def test_expression_after_number(self):
        self.assertTokens("(not 123)", [
            Token('expression start'),
            Token('word', 'not'),
            Token('number', 123),
            Token('expression end')
        ])

    def test_consecutive_nested_expression(self):
        self.assertTokens("((not 123))", [
            Token('expression start'),
            Token('expression start'),
            Token('word', 'not'),
            Token('number', 123),
            Token('expression end'),
            Token('expression end')
        ])
