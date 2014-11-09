import ast


def handle_assignment(target, value):
    print 'assign!'
    target_ast = target.ast
    target_ast.ctx = ast.Store()
    return ast.Assign(targets=[target_ast], value=value.ast)
    

def handle_addition(left, right):
    print 'add!'
    left_ast = left.ast
    left_ast.ctx = ast.Load()
    right_ast = right.ast
    right_ast.ctx = ast.Load()
    return ast.BinOp(left=left_ast, op=ast.Add(), right=right_ast)

def handle_print(target):
    print 'print!'
    target_ast = target.ast
    target_ast.ctx = ast.Load()
    return ast.Print(dest=None, values=[target_ast], nl=True)

def handle_expr(value):
    return value.ast

def handle_if(test):
    return ast.Num(n=1)
    #return ast.If(test.ast, body.ast)

def handle_else():
    return ast.Num(n=1)
    
signature_map = {
    'let _ be _': handle_assignment,
    '_ + _': handle_addition,
    'print _': handle_print,
    'if _': handle_if,
    'else': handle_else,
    # TODO this is a little weird. could be cleaned up?
    '_': handle_expr,
}
