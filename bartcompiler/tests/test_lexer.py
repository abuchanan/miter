import logging
import unittest

from bartcompiler import lexer


logging.basicConfig(level=logging.DEBUG)


def lex(s):
    return list(lexer.Lexer().lex(s))


class LexerTests(unittest.TestCase):

    def test_words(self):
        tokens = lex('one two')
        self.assertEqual(tokens, [
            lexer.Token('word', 'one'),
            lexer.Token('word', 'two'),
        ])

    def assertTokens(self, s, expected):
        self.assertEqual(lex(s), expected)

    def test_skip_leading_whitespace(self):
        self.assertTokens('   one two', [
            lexer.Token('word', 'one'),
            lexer.Token('word', 'two'),
        ])

    def test_skip_trailing_whitespace(self):
        self.assertTokens('one two   ', [
            lexer.Token('word', 'one'),
            lexer.Token('word', 'two'),
        ])

    def test_IDs(self):
        self.assertTokens("'one' 'two and three'", [
            lexer.Token('ID', 'one'),
            lexer.Token('ID', 'two and three'),
        ])

    def test_words_and_IDs(self):
        self.assertTokens("'one' and  'two and three' and four", [
            lexer.Token('ID', 'one'),
            lexer.Token('word', 'and'),
            lexer.Token('ID', 'two and three'),
            # TODO should these come as one token?
            lexer.Token('word', 'and'),
            lexer.Token('word', 'four'),
        ])

    def test_single_quote_in_word(self):
        with self.assertRaises(lexer.InvalidWord_SingleQuote):
            lex("word'")

        with self.assertRaises(lexer.InvalidWord_SingleQuote):
            lex("word'fo")

    def test_multiline(self):
        self.assertTokens("one\ntwo", [
            lexer.Token('word', 'one'),
            lexer.Token('newline', ''),
            lexer.Token('word', 'two'),
        ])

        self.assertTokens("'one'\n'two'", [
            lexer.Token('ID', 'one'),
            lexer.Token('newline', ''),
            lexer.Token('ID', 'two'),
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
            lexer.Token('ID', 'foo bar')
        ])

    def test_plus_sign_as_word(self):
        self.assertTokens('x + y', [
            lexer.Token('word', 'x'),
            lexer.Token('word', '+'),
            lexer.Token('word', 'y'),
        ])

    def test_minus_sign_as_word(self):
        self.assertTokens('x - y', [
            lexer.Token('word', 'x'),
            lexer.Token('word', '-'),
            lexer.Token('word', 'y'),
        ])
