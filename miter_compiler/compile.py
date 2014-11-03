



# stmt: def
#
# def: "define"
#
# id: '[A-Za-z]+'
#
# word: [A-Za-z]+
#
# expression: (id | word)*
#
# return: "return" expression

def iter_characters(lines):
    for line in lines:
        for c in line:
            yield c




def source_to_tokens(lines):
    current_token = ''

    # TODO NEXT need to decide whether the tokenizer is smart: does it know about
    # the syntax/format of certain types of tokens? Is just simply splitting on
    # whitespace enough? Does it look for the single quotes of an id and therefore
    # return an IdToken instance? Or does it just return strings?
    for c in iter_characters(lines):
        if is_whitespace(c):
            if current_token:
                yield current_token
                current_token = ''
        else:
           

    # TODO emit tokens for indentation

def tokens_to_ast(tokens):
    pass

def compile_ast(ast):
    pass
