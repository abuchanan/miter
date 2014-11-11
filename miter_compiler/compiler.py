import llvm.core as llvm


class ASTNodeVisitor(object):

    def visit(self, node):
        node_type_name = node.__class__.__name__
        method_name = 'transform_' + node_type_name
        try:
            method = getattr(self, method_name)
        except KeyError:
            raise Exception('Unrecognized AST node type: ' + node_type_name)
        else:
            return method(node)


    def transform_ID(self, node):
        pass

    def transform_Number(self, node):
        return llvm.Constant.int(llvm.Type.int(16), node.value)

    def transform_AdditionExpression(self, node):
        args = [self.visit(arg) for arg in node.args]
        return self.builder.add(args[0], args[1], 'tmp')

    def transform_AssignmentExpression(self, node):
        pass

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
