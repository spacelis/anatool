#!python
# -*- coding: utf-8 -*-
"""File: timeweb.py
Description:
History:
0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

from matplotlib import pyplot as plt

from anatool.analysis.timemodel import TimeModel
from anatool.analysis.textmodel import LanguageModel
from anatool.analysis.ranking import ranke, linearjoin
from anatool.analysis.evaluation import batcheval
from anatool.dm.dataset import Dataset, loadrows
from anatool.dm.db import GEOTWEET

def cmptimeweb(places, numtwts, numtest):
    """ compare the time model + web model to original pure text model
    """
    lms = [dict() for i in range(len(numtwts))]
    tms = [dict() for i in range(len(numtwts))]
    wms = dict()
    test = Dataset()
    for pid in places:
        twtp = loadrows(GEOTWEET, ('place_id', 'text', 'created_at'),
                ('place_id=\'{0}\''.format(pid),), 'sample',
                'order by rand() limit {0}'.format(max(numtwts) + numtest))
        for i in range(len(numtwts)):
            lms[i][pid] = LanguageModel(twtp['text'][:numtwts[i]])
            tms[i][pid] = TimeModel(twtp['created_at'][:numtwts[i]])
        web = loadrows(GEOTWEET, ('place_id', 'web'),
                ('place_id=\'{0}\''.format(pid),), 'web',
                'order by rand() limit 30')
        wms[pid] = LanguageModel(web['web'])

        # test data
        for i in range(max(numtwts) + 1, max(numtwts) + numtest):
            test.append({'label': pid,
                'lm': LanguageModel([twtp['text'][i],]),
                'tm': TimeModel([twtp['created_at'][i],])})

    # rank
    lmranks = [list() for i in range(len(numtwts))]
    tmranks = [list() for i in range(len(numtwts))]
    wmranks = list()
    for item in test:
        for i in range(len(numtwts)):
            lmranks[i].append(ranke(lms[i], item['lm']))
            tmranks[i].append(ranke(tms[i], item['tm']))
        wmranks.append(ranke(wms, item['lm']))
    lmtmranks = [list() for i in range(len(numtwts))]
    wmlmtmranks = [list() for i in range(len(numtwts))]
    for i in range(len(numtwts)):
        for ranklm, ranktm in zip(lmranks[i], tmranks[i]):
            lmtmranks[i].append(linearjoin([ranklm, ranktm], [0.5, 0.5]))
        for ranklm, ranktm, rankwm in zip(lmranks[i], tmranks[i], wmranks):
            wmlmtmranks[i].append(\
                    linearjoin([ranklm, ranktm, rankwm], [0.4, 0.3, 0.3]))

    # plot
    candls = ['-', '--']
    for i in range(len(numtwts)):
        plt.subplot(121 + i)
        plt.title('$t={0}$'.format(numtwts[i]))
        lmeval = batcheval(lmranks[i], test['label'])
        plt.plot(lmeval['pos'], lmeval['rate'],
                label='tweet',
                ls=candls[i], marker='o')
        lmtmeval = batcheval(lmtmranks[i], test['label'])
        plt.plot(lmtmeval['pos'], lmtmeval['rate'],
                label='tweet+time',
                ls=candls[i], marker='^')
        wmlmtmeval = batcheval(wmlmtmranks[i], test['label'])
        plt.plot(wmlmtmeval['pos'], wmlmtmeval['rate'],
                label='tweet+time+web',
                ls=candls[i], marker='*')
        plt.legend(loc='lower right')
    plt.show()


def run():
    """ Test this module
    """
    with open('chicago10.lst') as fin:
        cmptimeweb([p.strip() for p in fin], [100, 5], 10)

if __name__ == '__main__':
    run()





