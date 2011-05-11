#!python
# -*- coding: utf-8 -*-
"""File: annotation.py
Description:
    This module contains several annotations for easing programming
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'


import logging, inspect
from heapq import nsmallest
from operator import itemgetter

class LogFunction(object):
    """Log before entering a function"""
    def __init__(self, msg):
        super(LogFunction, self).__init__()
        self.msg = msg

    def __call__(self, func):
        """Decorating the function"""
        def wraped_func(*args, **kargs):
            """Wrapping function"""
            callarg = inspect.getcallargs(func, *args, **kargs)
            logging.info(self.msg)
            for item in callarg.iteritems():
                logging.info(self.msg + '::'\
                        + str(item[0]) + ':' + str(item[1]))
            func(*args)
        return wraped_func

class Cache(object):
    """Cache results for stateless functions"""
    def __init__(self, poolsize=50):
        super(Cache, self).__init__()
        self.poolsize = poolsize
        self.pool = dict()
        self.life = dict()
        self.ttl = 0

    def __call__(self, func):
        """Decorating the function"""
        def wraped_func(*args, **kargs):
            """Wrapping function"""
            callarg = inspect.getcallargs(func, *args, **kargs)
            strarg = str(callarg)
            if strarg not in self.pool:
                self.pool[strarg] = func(*args, **kargs)
                self.life[strarg] = self.ttl
                self.ttl += 1
            if len(self.pool) > self.poolsize:
                item = nsmallest(1, self.life.iteritems(), key=itemgetter(1))[0]
                del self.pool[item[0]]
                del self.life[item[0]]
            return self.pool[strarg]
        return wraped_func

def test():
    @Cache()
    def cfunc(x, y=1, **karg):
        print 'func', x, y
        return x + y
    print cfunc(1, 1, key='haha')
    print cfunc(1)
    print cfunc(1, 2)
    print cfunc(1)
    print cfunc(1, 1)


if __name__ == '__main__':
    test()
