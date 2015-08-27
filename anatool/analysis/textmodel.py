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
from anatool.analysis.feature import norm_v1, bgdist, f_tf
from anatool.dm.dataset import Dataset, DataItem

class LanguageModel(DataItem):
    """ Language model is a statistical model for text which capture term
        frequency as featuers
    """
    def __init__(self, text):
        super(LanguageModel, self).__init__(norm_v1(bgdist(f_tf(text))))

    @classmethod
    def kl_divergence(cls, lm, lmref):
        """get the KL-divergence(lm || lmref) = sigma_i(lm(i)*log(lm(i)/lmref(i)))
        """
        if not (isinstance(lm, cls) and isinstance(lmref, cls)):
            raise TypeError
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

    def score(self, lm, **kargs):
        """ Return KL-divergences as scores
        """
        return LanguageModel.kl_divergence(lm, self)

    def isasc(self):
        """ Return 1 indicating the smaller value means more similar
        """
        return True

class TermSetModel(set):
    """ TermSetModel is a model capturing the topical terms
    """
    def __init__(self, text):
        super(TermSetModel, self).__init__(bgdist(f_tf(text)))

    def score(self, tms, **kargs):
        """ Return |self n tms| / |self U tms|
        """
        return len(self & tms) / float(len(self | tms))

    def isasc(self):
        """ Return 0 indicating the smaller value means more similar
        """
        return False


class BiasTermSetModel(TermSetModel):
    """ TermSetModel is a model capturing the topical terms
    """
    def __init__(self, text):
        super(BiasTermSetModel, self).__init__(text)

    def score(self, tms, **kargs):
        """ Return |self n tms| / |self U tms|
        """
        return len(self & tms) / float(len(self))

    def isasc(self):
        """ Return 0 indicating the smaller value means more similar
        """
        return False


def test():
    """test
    """
    lm = LanguageModel(('good test', 'bad test'))
    lmref = LanguageModel(('well test, test',))
    print lm
    print lmref
    print lm.score(lmref)

if __name__ == '__main__':
    test()
