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

import math
from anatool.dm.dataset import DataItem, Dataset
from anatool.analysis.text_util import to_unicode, fourq_filter

from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer
_ANALYZER = StemmingAnalyzer()
# Alternative analyzer could be used
#from anatool.analysis.stopwords import STOPWORDS_RANKSNL_LONG
#_ANALYZER = StandardAnalyzer(stoplist = STOPWORDS_RANKSNL_LONG)

def get_tokens(line):
    """ return the token list of the line
    """
    line = fourq_filter(line)
    line = to_unicode(line)
    tokens = [token.text for token in _ANALYZER(line)]
    return tokens

def token_freq(token_lst):
    """Return the token distribution"""
    dist = DataItem()
    for t in token_lst:
        if t not in dist:
            dist[t] = 1
        else:
            dist[t] += 1
    return dist

def line2tf(line):
    """shortcut for token_freq(get_tokens())"""
    return token_freq(get_tokens(line))

#--------------------------------------------------------------- Utils
def count_non_zero(vector):
    """Count the number of non-zero values in the vector
        @arg vector list() of integers
        @return the number of non-zero values
    """
    cnt = 0
    for val in vector:
        if val != 0:
            cnt += 1
    return cnt

def idf(dset):
    """get the idf distribution
        @arg dset Dataset() of term vectors
        @return DataItem() of term -> IDF values
    """
    idfdist = DataItem()
    for key in dset.iterkeys():
        idfdist[key] = count_non_zero(dset[key])
    return idfdist

def bgdist(dset):
    """get the back ground distribution
        @arg dset Dataset() of term vectors
        @return DataItem() of term -> tf values in the whole corpus
    """
    dist = DataItem()
    for key in dset.iterkeys():
        dist[key] = sum(dset[key])
    return dist

#--------------------------------------------------------------- Features
def f_tf(text):
    """get the term frequency feature
        @arg text list() of str()
        @return Dataset() of term vectors
    """
    dset = Dataset()
    for line in text:
        dset.append(line2tf(line))
    return dset

def f_tfidf(text):
    """get the TFIDF weights for each term vectors in dset
        Fomula tfidf = tf/idf
        @arg text list() of str()
        @return Dataset() of term vectors in TFIDF scale
    """
    dset = f_tf(text)
    idfdist = idf(dset)
    for key in dset.iterkeys():
        for idx in range(len(text)):
            dset[key][idx] /= idfdist[key]
    return dset

def f_tfidf_logidf(text):
    """get the TFIDF weights for each term vectors in dset
        Fomula tfidf = tf*log(N/idf)
        @arg text list() of str()
        @return Dataset() of term vectors in TFIDF scale
    """
    dset = f_tf(text)
    idfdist = idf(dset)
    for key in dset.iterkeys():
        for idx in range(len(text)):
            dset[key][idx] *= math.log(len(text)/idfdist[key])
    return dset

def norm_e(dset):
    """normalize values in element wise, i.e., column normalization
        @arg dset Dataset() of vectors
        @return Dataset() of vectors normalized
    """
    ndset = Dataset()
    for key in dset.iterkeys():
        maxval = max(dset[key])
        ndset[key] = list()
        for val in dset[key]:
            ndset[key].append(val/maxval)
    return ndset

def norm_v2(dset):
    """normalize values in vector wise, row normalization (L_2)
        @arg dset Dataset() of vectors
        @return Dataset() of vectors normalized
    """
    ndset = Dataset()
    for idx in range(dset.size()):
        sqrval = math.sqrt(sum(dset[key][idx]**2 for key in dset))
        item = DataItem()
        for key in dset.iterkeys():
            item[key] = dset[key][idx] / sqrval
        ndset.append(item)
    return ndset

def norm_v1(ditem):
    """normalize values in a vector, normalization L_1
        @arg dset DataItem() of vector
        @return Dataset() of vectors normalized
    """
    nditem = DataItem()
    sumval = sum(ditem[key] for key in ditem)
    for key in ditem:
        nditem[key] = float(ditem[key]) / sumval
    return nditem

def test():
    """docstring for test
    """
    print norm_v1(bgdist(f_tf(('This is a test for term vectors for and a to',))))

if __name__ == '__main__':
    test()
