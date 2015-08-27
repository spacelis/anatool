#!python
# -*- coding: utf-8 -*-
"""File: distinguish.py
Description:
    Verify whether the places are distinguishable by language models.
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from anatool.analyze.dataset import place_name
from anatool.analyze.lm import lmfromtext, kl_divergence
from anatool.experiment.websmooth import webmodel, twtmodel
from anatool.dm.db import CONN_POOL, GEOTWEET

def confusionmatrix(places):
    """ Show the matrix of confusion between LMs by KL-divergence
    """
    lmtwt1 = dict()
    lmtwt2 = dict()
    for pid in places:
        cur = CONN_POOL.get_cur(GEOTWEET)
        cur.execute('select text from sample' \
                ' where place_id = \'{0}\' order by rand() limit {1}'.format(pid, 200))
        text = [row['text'] for row in cur]
        lmtwt1[pid] = lmfromtext(text[:80])
        lmtwt2[pid] = lmfromtext(text[81:160])
    confmat = list()
    for lm_i in places:
        confmat.append([kl_divergence(lmtwt1[lm_i], lmtwt2[lm_j]) for lm_j in places])

    selfavg = sum([confmat[i][i] for i in range(len(places))])
    mutavg = sum([sum(confmat[i]) for i in range(len(places))]) - selfavg
    selfavg /= float(len(places))
    mutavg /= float(len(places)*len(places) - len(places))
    print selfavg, mutavg


    plt.imshow(np.array(confmat), cmap = cm.gray, interpolation='nearest')
    plt.yticks(range(len(places)), \
            ['{0}: {1}'.format(place_name(places[i]), i) for i in range(len(places))])
    plt.xticks(range(len(places)))
    plt.subplots_adjust(left=0.4)
    plt.colorbar(shrink=0.66)
    plt.savefig('sf_confm.eps')
    plt.show()

if __name__ == '__main__':
    confusionmatrix([p.strip() for p in open('sanfrancisco10.lst')])

