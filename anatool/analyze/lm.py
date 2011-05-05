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
from anatool.analyze.feature import norm_vp, bgdist, f_tf
from anatool.analyze.dataset import Dataset, DataItem

def lmfromtext(text):
    """generate a language model from the text
        @arg text list() of str()
        @return
    """
    return norm_vp(bgdist(f_tf(text)))

def kl_divergence(lm, lmref):
    """get the KL-divergence(lm || lmref) = sigma_i(lm(i)*log(lm(i)/lmref(i)))
    """
    dgc = 0.0
    for key in lmref:
        if key in lm:
            dgc += lm[key] * math.log(lm[key] / lmref[key])
    return dgc


