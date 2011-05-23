#!python
# -*- coding: utf-8 -*-
"""File: evaluation.py
Description:
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

from anatool.dm.dataset import Dataset
def evaluate(ranks, expects, pos):
    """ Evaluate the ranking algorithms seeing the expected place_id in the
        rank higher than given pos
        @arg ranks list() of ranks returned by webguess()
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

