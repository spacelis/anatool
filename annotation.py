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


import logging, inspect, os
from heapq import nsmallest
from operator import itemgetter
try:
    import cpickle as pickle
except ImportError:
    import pickle

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


class Cache2(object):
    """Cache results for stateless functions"""
    #TODO check whether it will work

    _DISABLED = False
    _CACHES = list()
    _CACHEFILES = set()

    @classmethod
    def drop_all(cls):
        """Drop all caches
        """
        for che in Cache2._CACHES:
            che.pool = dict()

    @classmethod
    def disable(cls):
        """Disable the cache system
        """
        cls._DISABLED = True

    @classmethod
    def enable(cls):
        """Disable the cache system
        """
        cls._DISABLED = False

    def __init__(self, **karg):
        super(Cache2, self).__init__()
        Cache2._CACHES.append(self)
        _karg = {'poolsize': 50, 'base': None}
        _karg.update(karg)

        self.poolsize = _karg['poolsize']
        self.pool = dict()
        self.ttl = dict()
        self.tick = 0
        self.base = _karg['base']

        if _karg['base']:
            if _karg['base'] not in Cache2._CACHEFILES:
                Cache2._CACHEFILES.add(_karg['base'])
            else:
                raise Exception, 'Basefiles conflicts [{0}]'.\
                        format(_karg['base'])
            if os.path.exists(_karg['base']):
                with open(_karg['base'],'rb') as basefile:
                    self.poolsize, self.pool, self.ttl, self.tick = pickle.load(
                        basefile)
                self.base = _karg['base']

    def __call__(self, func):
        """Decorating the function"""
        def wraped_func(*args, **kargs):
            """Wrapping function"""
            if Cache2._DISABLED:
                return func(*args, **kargs)
            callarg = inspect.getcallargs(func, *args, **kargs)
            strarg = str(callarg)
            if strarg not in self.pool:
                self.pool[strarg] = func(*args, **kargs)
                self.ttl[strarg] = self.tick
                self.tick += 1
            if len(self.pool) > self.poolsize:
                item = nsmallest(1, self.ttl.iteritems(), key=itemgetter(1))[0]
                del self.pool[item[0]]
                del self.ttl[item[0]]
            return self.pool[strarg]
        return wraped_func

    def __del__(self):
        """docstring for __del__
        """
        with open(self.base, 'wb') as basefile:
            pickle.dump([self.poolsize, self.pool, self.ttl, self.tick],
                basefile)

def test():
    @Cache2(base='test.pic')
    def cfunc(x, y=1, **karg):
        print 'func', x, y
        return x + y
    Cache2.disable()
    Cache2.drop_all()
    print cfunc(1, 1, key='haha')
    print cfunc(1)
    Cache2.enable()
    print cfunc(1, 2)
    print cfunc(1)
    print cfunc(1, 1)


if __name__ == '__main__':
    test()
