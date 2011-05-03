#!python
# -*- coding: utf-8 -*-
"""File: feature.py
Description:
    This module provides a set of functions for abstract features from raw data
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

from anatool.dataset import DataItem, Dataset


#--------------------------------------------------------------- Utils
def count_non_zero(lst):
    """Count the number of non-zero values in the lst
    """
    cnt = 0
    for val in lst:
        if val != 0:
            cnt += 1
    return cnt

#--------------------------------------------------------------- Features
def idf(ds):
    """get the idf distribution"""
    idfdist = DataItem()
    for key in ds:
        idfdist[key] = count_non_zero(ds[key])
    return idfdist

def bgdist(ds, keylist):
    """get the back ground distribution
    """
    bgdist = DataItem()
    for key in keylist:
        bgdist[key] = sum(ds[key])
    return bgdist

