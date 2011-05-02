#!python
# -*- coding: utf-8 -*-
"""File: log_helper.py
Description:
    This module contains several annotations for easing logging
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'


import logging
import inspect

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

