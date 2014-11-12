import argparse
import logging

from miter_compiler import jit


#logging.basicConfig(level=logging.DEBUG)

cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('source_file', type=argparse.FileType('r'))


if __name__ == '__main__':
    args = cli_parser.parse_args()
    source_code = args.source_file.read()
    jit.run(source_code)
