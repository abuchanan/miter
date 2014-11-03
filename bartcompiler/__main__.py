import argparse
import itertools

from bartcompiler.lexer import Lexer


parser = argparse.ArgumentParser()
parser.add_argument('source_file', type=argparse.FileType('r'))


def iter_lines(tokens):

    while True:
        # Drop leading newlines
        tokens = itertools.dropwhile(lambda t: t.type == 'newline', tokens)
        l = list(itertools.takewhile(lambda t: t.type != 'newline', tokens))
        if l:
            yield l
        else:
            raise StopIteration


if __name__ == '__main__':
    args = parser.parse_args()
    source_code = args.source_file.read()

    tokens = Lexer().lex(source_code)

    for line in iter_lines(tokens):
        print line
