import logging
import os
import re
import sys
import tempfile
import time
import unittest

from miter_compiler import jit

this_dir = os.path.dirname(__file__)
scripts_dir = os.path.join(this_dir, 'scripts')


def capture_jit_output(*args):
    """
    Run the Miter source code via the JIT, capturing and returning its output.
    """

    # Since the JIT (and Miter) runs via C code, we need to do a little
    # extra in order to capture STDOUT.
    # Replace the STDOUT file descriptor with our capturing file.
    sys.stdout.flush()
    cap = tempfile.TemporaryFile()
    stdout_fileno = sys.stdout.fileno()
    old_stdout = os.dup(stdout_fileno)
    os.dup2(cap.fileno(), stdout_fileno)

    jit.run(*args)

    # Restore stdout file descriptor to original
    sys.stdout.flush()
    os.dup2(old_stdout, stdout_fileno)

    # Get the captured content
    cap.seek(0)
    content = cap.read()
    cap.close()

    return content
    

def create_script_test(source, expected):
    
    def test_method(testcase):
        captured = capture_jit_output(source)
        testcase.assertEqual(captured, expected)

    return test_method


def script_paths():
    """
    Generate paths to Miter scripts in the ./scripts/ directory
    """
    for p in os.listdir(scripts_dir):
        path = os.path.join(scripts_dir, p)

        if os.path.isfile(path) and path.endswith('.mtr'):
            yield path


def generate_test_methods(paths):
    """
    Generate test methods for all script paths
    """
    for path in paths:
        content = open(path).read()
        s = re.split('^expected output:\n', content, flags=re.MULTILINE)

        if len(s) != 2:
            logging.warning('Script test: no expected output found for ' + path)
        else:
            source, expected = s
            test_method = create_script_test(source, expected)
            test_method.__name__ = 'test_' + os.path.relpath(path, this_dir)
            yield test_method


class ScriptTests(unittest.TestCase):

    def __metaclass__(name, bases, dict):
        paths = script_paths()
        for method in generate_test_methods(paths):
            dict[method.__name__] = method
        return type(name, bases, dict)
