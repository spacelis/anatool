#!python
# -*- coding: utf-8 -*-
"""File: ranking.py
Description:
    Rank candidates by scoring method
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import random
from operator import itemgetter
from anatool.dm.dataset import Dataset

def unitscore(vector):
    """ Map all values in vector into [0, 1]
        a^'_i = (a_i - m) / n where m is the min(vector), n = max(vector) -
        min(vecotr) and make a compensate if needed
        @arg vector a list() of numbers
        @return a list() of numbers reunited
    """
    vecmin = vector[0]
    vecmax = vector[-1]
    if vecmin == vecmax:
        return [1 for val in vector]
    return [float(val - vecmin) / (vecmax - vecmin) for val in vector]

#--------------------------------------------------------------- Experiment

def ranke(cand, ref, **kargs):
    """ Rank the models in cand according to the scoring methods in the models
        @arg cand dict() of (label, model)
        @arg ref model for testing
        @return an ordered Dataset() of {'label', 'score'}
    """
    rak = list()
    for lbl in cand.iterkeys():
        rak.append((lbl, cand[lbl].score(ref, **kargs)))
    rak = sorted(rak, key=itemgetter(1), reverse=not ref.isasc())
    res = Dataset()
    for item in rak:
        res.append({'label': item[0], 'score': item[1]})
    return res

def randranke(cand):
    """ Return a random sorted cand
    """
    rak = list()
    for lbl in cand:
        rak.append((lbl, random.random()))
    rak = sorted(rak, key=itemgetter(1))
    res = Dataset()
    for item in rak:
        res.append({'label': item[0], 'score': item[1]})
    return res



def linearjoin(ranks, balance):
    """ Join a set of ranks by the weights in balance
        @arg ranks a list() of ranks that need to combine
        @arg balance a list() of floats indicating combine weights
        @return a combined rank

    """
    for rak in ranks:
        rak['score'] = unitscore(rak['score'])

    sortedranks = [[item for item in r.sorted_items('label')] for r in ranks]
    unitrank = list()
    for idx in range(len(sortedranks[0])):
        unitrank.append((sortedranks[0][idx]['label'],
            sum([score * bl for score, bl in \
                zip([sortedranks[i][idx]['score'] for i in range(len(sortedranks))],
                        balance)])))
    unitrank = sorted(unitrank, key=itemgetter(1), reverse=False)
    res = Dataset()
    for item in unitrank:
        res.append({'label': item[0], 'score': item[1]})
    return res

def test():
    """ Test this module
    """
    print unitscore([0.9, 0.7, 0.6])
    print unitscore([0.6, 0.7, 0.9])



if __name__ == '__main__':
    test()
