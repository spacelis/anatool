#!python
# -*- coding: utf-8 -*-
"""File: evaluation.py
Description:
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

#from scipy.stats.morestats import wilcoxon
from statlib.stats import lwilcoxont
from operator import itemgetter
from anatool.dm.dataset import Dataset

def evaluate(ranks, expects, pos):
    """ Evaluate the ranking algorithms seeing the expected place_id in the
        rank higher than given pos
        @arg ranks list() of ranks returned by ranke()
        @arg expects list() of expected labels
        @arg pos the given position seen as length of system returned
        @return the rate of goals
    """
    goal = 0
    for expr in range(len(ranks)):
        if expects[expr] in set(ranks[expr]['label'][:pos]):
            goal += 1
    return float(goal) / len(ranks)

def batcheval(ranks, expects, maxpos=-1):
    """ The batch version of evaluate() which test a set of pos
        @arg ranks list() of ranks returned by webguess()
        @arg expects list() of expected labels
        @arg maxpos the max position
        @return a list of rates of goals
    """
    if maxpos == -1:
        maxpos = ranks[0].size()
    goalrates = Dataset()
    for pos in range(maxpos + 1):
        goalrates.append({'pos': pos, 'rate': evaluate(ranks, expects, pos)})
    return goalrates

def wilcoxontest(ranks_a, ranks_b, expects):
    """ Return wilcoxon p values of ranks_a and ranks_b
        @arg ranks_a a list() of ranks(dataset(){'label', 'score'})
        @arg ranks_b a list() of ranks(dataset(){'label', 'score'})
        @arg expects a list() of testitems(dataset(){'label', ...})
        @return p-value of two tailed wilcoxon teset
    """
    rak_x = list()
    rak_y = list()
    for i in range(expects.size()):
        for j in range(ranks_a[i].size()):
            if ranks_a[i]['label'][j] == expects['label'][i]:
                rak_x.append(j)
                break
        for j in range(ranks_b[i].size()):
            if ranks_b[i]['label'][j] == expects['label'][i]:
                rak_y.append(j)
                break
    sval, pval = lwilcoxont(rak_x, rak_y)
    #sval, pval = wilcoxon(rak_x, rak_y)
    return pval

def placetotalrank(ranks, expects):
    """ Return the sum of position of reference POIs in ranks
        @arg ranks a list() of ranks(dataset(){'label', 'score'})
        @arg expects a list() of testitems(dataset(){'label', ...})
        @return a sorted dataset(){'label', 'totalrank'}
    """
    plcrak = dict()
    for i in range(expects.size()):
        if expects['label'][i] not in plcrak:
            plcrak[expects['label'][i]] = 0
        for j in range(ranks[i].size()):
            if ranks[i]['label'][j] == expects['label'][i]:
                plcrak[expects['label'][i]] += j
                break
    items = sorted(plcrak.iteritems(), key=itemgetter(1))
    res = Dataset()
    for item in items:
        res.append({'label': item[0], 'totalrank': item[1]})
    return res






def wilconxontest(rate_a, rate_b):
    """ generate a value to say whether there is a statistical significance be
        tween ranka and rankb
    """
    if len(rate_a) != len(rate_b):
        raise ValueError('Two rankings are not of same length.')
    rank = filter(lambda x: x!=0, sorted([a - b for a, b in zip(rate_a, rate_b)],
                    key=lambda x: abs(x)))
    if len(rank) == 0:
        return 0.0
    cumrank = 1.0
    sign = [rank[i]/abs(rank[i]) for i in range(len(rank))]
    val = rank[0]
    st = 0
    normrank = list()
    for i in range(1, len(rank)):
        if abs(rank[i]) == val:
            cumrank += float(i + 1)
        else:
            normrank.extend([sign[j] * cumrank/(i-st) for j in range(st, i)])
            st = i
            val = abs(rank[i])
            cumrank = float(i + 1)
    normrank.extend([sign[j] * cumrank/(len(rank)-st) for j in range(st, len(rank))])

    print normrank

    wpos, wnag = 0.0, 0.0
    wpos = sum(filter(lambda x: x>0, normrank))
    wnag = - sum(filter(lambda x: x<0, normrank))
    return len(rate_a), min(wpos, wnag)



if __name__ == '__main__':
    print lwilcoxont([125, 115, 130, 140, 140, 115, 140, 125, 140, 135],
                    [110, 122, 125, 120, 140, 124, 123, 137, 135, 145])




