import ast
import logging

from miter_compiler import compiler, lexer


logging.basicConfig(level=logging.DEBUG)


def lex(s):
    return list(lexer.Lexer().lex(s))


class CompilerTests(unittest.TestCase):

    def assertAST(self, source, expected_dump):
        tokens = lex(source)
        tree = compiler.tokens_to_ast(tokens)
        dump = ast.dump(tree)
        self.assertEqual(dump, expected_dump)


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
