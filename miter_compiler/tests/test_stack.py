import unittest

from miter_compiler.stack import Stack


class StackTests(unittest.TestCase):

    def test_all(self):
        stack = Stack()
        self.assertEqual(stack.level, 0)
        self.assertEqual(stack.top, [])
        stack.top.append('foo')
        stack.save()
        self.assertEqual(stack.level, 1)
        self.assertEqual(stack.top, [])
        stack.restore()
        self.assertEqual(stack.level, 0)
        self.assertEqual(stack.top, ['foo'])
