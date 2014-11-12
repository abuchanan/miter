import argparse
import os

import llvm.core
import llvm.ee

from miter_compiler import compiler, lexer, parser


_this_dir = os.path.dirname(__file__)
std_so_path = os.path.join(_this_dir, 'std.bc')

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('source_file', type=argparse.FileType('r'))


if __name__ == '__main__':
    args = cli_parser.parse_args()
    source_code = args.source_file.read()

    tokens = lexer.source_to_tokens(source_code)
    ast = parser.tokens_to_ast(tokens)
    module = compiler.AST_to_IR(ast)

    print module

    std_mod = llvm.core.Module.from_bitcode(open(std_so_path).read())
    module.link_in(std_mod)

    engine = llvm.ee.ExecutionEngine.new(module)
    main_func = module.get_function_named('main')
    engine.run_function(main_func, [])
