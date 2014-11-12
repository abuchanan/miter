import llvm.core as llvm


class ASTNodeVisitor(object):

    def __init__(self):
        self.named_values = {}

    def visit(self, node):
        node_type_name = node.__class__.__name__
        method_name = 'transform_' + node_type_name
        try:
            method = getattr(self, method_name)
        except KeyError:
            raise Exception('Unrecognized AST node type: ' + node_type_name)
        else:
            return method(node)


    def alloca(self, var_name):
        current_function = self.builder.basic_block.function
        bb = current_function.get_entry_basic_block()
        builder = llvm.Builder.new(bb)
        builder.position_at_beginning(bb)
        return builder.alloca(llvm.Type.int(16), name=var_name)

    def transform_ID(self, node):
        # TODO need some refactoring of ID load/store
        # if node.context == 'store':
        # if node.context == 'load':
        var = self.named_values[node.value]
        return self.builder.load(var, node.value)

    def transform_Number(self, node):
        return llvm.Constant.int(llvm.Type.int(16), node.value)

    def transform_AdditionExpression(self, node):
        args = [self.visit(arg) for arg in node.args]
        return self.builder.add(args[0], args[1], 'tmp')

    def transform_Define(self, node):
        expr = node.value
        # TODO determine return type
        func_type = llvm.Type.function(llvm.Type.int(16),
                                       [llvm.Type.int(16)] * len(expr.args),
                                       False)

        func = llvm.Function.new(self.module, func_type, expr.signature)

        # TODO I forget, why do we need a new builder?
        old_builder = self.builder
        bb = func.append_basic_block('entry')
        self.builder = llvm.Builder.new(bb)

        for func_arg, expr_arg in zip(func.args, expr.args):
            func_arg.name = expr_arg.value
            alloca = self.alloca(func_arg.name)
            self.builder.store(func_arg, alloca)
            self.named_values[func_arg.name] = alloca

        for expression in node.block:
            self.visit(expression)

        func.verify()
        self.builder = old_builder
        self.named_values.clear()

    def transform_Return(self, node):
        val = self.visit(node.value)
        self.builder.ret(val)

    def transform_AssignmentExpression(self, node):
        ID_arg = node.args[0]
        value_arg = node.args[1]

        value = self.visit(value_arg)

        try:
            # TODO give the ID node better attribute name, s/value/name/
            var = self.named_values[ID_arg.value]
        except KeyError:
            var = self.alloca(ID_arg.value)
            self.named_values[ID_arg.value] = var

        self.builder.store(value, var)

        return value

    def transform_Expression(self, node):
        # TODO use extern and builtins to get rid of this
        #
        # OR maybe just declare every expression that is called, and leave
        #    it to the linker or runtime to decide whether the declaration/call
        #    is worth throwing an error?
        sig = node.signature
        if sig == 'print _':
            sig = 'miter_print'

        callee = self.module.get_function_named(sig)
        args = [self.visit(arg) for arg in node.args]
        return self.builder.call(callee, args)

    def transform_Module(self, node):
        self.module = llvm.Module.new(node.name) 

        main_func_type = llvm.Type.function(llvm.Type.void(), [])
        main_func = self.module.add_function(main_func_type, 'main')

        print_type = llvm.Type.function(llvm.Type.void(), [llvm.Type.int(16)])
        self.module.add_function(print_type, 'miter_print')

        bb = main_func.append_basic_block('entry')

        self.builder = llvm.Builder.new(bb)

        for expression in node.expressions:
            self.visit(expression)

        self.builder.ret_void()
        main_func.verify()

        return self.module


def AST_to_IR(ast):
    visitor = ASTNodeVisitor()
    module = visitor.visit(ast)
    return module
