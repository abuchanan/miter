import argparse
import ast
import itertools

from miter_compiler.lexer import Lexer


parser = argparse.ArgumentParser()
parser.add_argument('source_file', type=argparse.FileType('r'))


def handle_assignment(target_name, value):
    print 'assign!'
    targets = [ast.Name(id=target_name, ctx=ast.Store())]
    return ast.Assign(targets=targets, value=ast.Num(n=value))
    

def handle_addition(left_name, right_name):
    print 'add!'
    left = ast.Name(id=left_name, ctx=ast.Load())
    right = ast.Name(id=right_name, ctx=ast.Load())
    binop = ast.BinOp(left=left, op=ast.Add(), right=right)
    return ast.Expr(value=binop)


builtins = {
    'let _ be _': handle_assignment,
    '_ + _': handle_addition,
}


def iter_lines(tokens):

    while True:
        # Drop leading newlines
        tokens = itertools.dropwhile(lambda t: t.type == 'newline', tokens)
        l = list(itertools.takewhile(lambda t: t.type != 'newline', tokens))
        if l:
            yield l
        else:
            raise StopIteration


def hash_statement(tokens):
    h = []

    for token in tokens:
        if token.type == 'word':
            h.append(token.value)
        elif token.type == 'ID' or token.type == 'number':
            h.append('_')

    return ' '.join(h)


def get_vars(tokens):
    var_types = ('ID', 'number')
    return [token.value for token in tokens if token.type in var_types]
    

if __name__ == '__main__':
    args = parser.parse_args()
    source_code = args.source_file.read()

    tokens = Lexer().lex(source_code)

    body = []

    for line in iter_lines(tokens):
        h = hash_statement(line)
        print line
        var_values = get_vars(line)
        handler = builtins[h]
        s = handler(*var_values)
        body.append(s)

    mod = ast.Module(body=body)

    ast.fix_missing_locations(mod)

    ast.dump(mod)

    print eval(compile(mod, '<string>', 'exec'))
