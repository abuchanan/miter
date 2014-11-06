import ast
import logging
import unittest

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

    def test_nested_phrases(self):
        source = "if 'one' and ((not 'three') and (not 'two'))"

        self.assertAST(source, 
