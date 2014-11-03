import os

_this_dir = os.path.dirname(__file__)

def read(*args):
    path = os.path.join(_this_dir, *args)
    return open(path).read()
