# -*- coding: utf-8 -*-

__appname__ = 'Ascii Graph'
__author__ = "Jérémie Ferry <jerem.ferry@gmail.com>"
__licence__ = "BSD"
__website__ = "https://github.com/mothsART/asciigraph"
__version__ = '0.1'
VERSION = tuple(map(int, __version__.split('.')))


def interface(test=False):
    from .tty import TTYInterface
    return TTYInterface(test=test)
