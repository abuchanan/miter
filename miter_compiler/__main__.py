import argparse
import ast

from miter_compiler import compiler
from miter_compiler.lexer import Lexer


parser = argparse.ArgumentParser()
parser.add_argument('source_file', type=argparse.FileType('r'))


if __name__ == '__main__':
    args = parser.parse_args()
    source_code = args.source_file.read()

    tokens = Lexer().lex(source_code)
    tree = compiler.tokens_to_ast(tokens)

    ast.fix_missing_locations(tree)

    print ast.dump(tree)

    print eval(compile(tree, '<string>', 'exec'))
