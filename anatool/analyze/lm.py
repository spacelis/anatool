#!python
# -*- coding: utf-8 -*-
"""File: lm.py
Description:
    This module provide a set of functions facilitating language models.
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import math
from anatool.analyze.feature import norm_v1, bgdist, f_tf
from anatool.analyze.dataset import Dataset, DataItem

def lmfromtext(text):
    """generate a language model from the text
        @arg text list() of str()
        @return
    """
    dist = bgdist(f_tf(text))
    #keys = dist.keys()
    #for key in keys:
        #if dist[key] < 2:
            #del dist[key]
    return norm_v1(dist)

def kl_divergence(lm, lmref):
    """get the KL-divergence(lm || lmref) = sigma_i(lm(i)*log(lm(i)/lmref(i)))
    """
    dgc = 0.0
    keyset = set()
    for key in lm:
        keyset.add(key)
    for key in lmref:
        keyset.add(key)
    for key in keyset:
        p = lm[key] if key in lm else 1e-100
        q = lmref[key] if key in lmref else 1e-100
        dgc += p * math.log(p / q)
    return dgc

def test():
    """test
    """
    lm = lmfromtext(('good test', 'bad test'))
    lmref = lmfromtext(('well test, test',))
    print lm
    print lmref
    print kl_divergence(lm, lmref)

if __name__ == '__main__':
    test()
