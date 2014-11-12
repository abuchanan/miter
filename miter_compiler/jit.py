import logging
import os

import llvm.core
import llvm.ee

from miter_compiler import compiler, lexer, parser


_this_dir = os.path.dirname(__file__)
std_so_path = os.path.join(_this_dir, 'std.so')
std_bc_path = os.path.join(_this_dir, 'std.bc')


def run(source_code):
    tokens = lexer.source_to_tokens(source_code)
    ast = parser.tokens_to_ast(tokens)
    module = compiler.AST_to_IR(ast)

    std_mod = llvm.core.Module.from_bitcode(open(std_bc_path).read())
    module.link_in(std_mod)

    #llvm.core.load_library_permanently(std_so_path)

    logging.debug('\n' + str(module))

    engine = llvm.ee.ExecutionEngine.new(module)
    main_func = module.get_function_named('main')
    engine.run_function(main_func, [])
