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
from anatool.analysis.ranking import ranke, linearjoin, randranke
from anatool.analysis.evaluation import batcheval, wilcoxontest, placetotalrank
from anatool.dm.dataset import Dataset, loadrows, place_name
from anatool.dm.db import GEOTWEET

import seaborn as sns
sns.set_palette("deep", desat=.6)
sns.set_style("white")
sns.set_context(font_scale=1.5, rc={"figure.figsize": (3, 2), 'axes.grid': False, 'axes.linewidth': 1,})

def cmptimeweb(cities, numtwts, numtest):
    """ compare the time model + web model to original pure text model
    """
    lmranks = [list() for _ in numtwts]
    tmranks = [list() for _ in numtwts]
    wmranks = list()
    randranks = list()
    lmtmranks = [list() for _ in numtwts]
    wmlmranks = [list() for _ in numtwts]
    wmlmtmranks = [list() for _ in numtwts]
    test = Dataset()

    for city in cities:
        lms = [dict() for _ in numtwts]
        tms = [dict() for _ in numtwts]
        wms = dict()
        tst = Dataset()
        for pid in city:
            twtp = loadrows(GEOTWEET, ('place_id', 'text', 'created_at'),
                            ('place_id=\'{0}\''.format(pid),), 'sample_switch_place_cate',
                            'order by rand() limit {0}'.format(max(numtwts) + numtest))
            for i, n in enumerate(numtwts):
                lms[i][pid] = LanguageModel(twtp['text'][:n])
                tms[i][pid] = TimeModel(twtp['created_at'][:n])
            web = loadrows(GEOTWEET, ('place_id', 'web'),
                           ('place_id=\'{0}\''.format(pid),), 'web',
                           'order by rand() limit 30')
            try:
                wms[pid] = LanguageModel(web['web'])
            except KeyError:
                wms[pid] = LanguageModel('')

            # Prepare test data by the tail part of the data retrieved from db
            test_pos = max(numtwts)
            for i in range(test_pos, test_pos + numtest):
                tst.append({'label': pid,
                            'lm': LanguageModel([twtp['text'][i],]),
                            'tm': TimeModel([twtp['created_at'][i],])})

        test.extend(tst)
        # rank
        for item in tst:
            for i, _ in enumerate(numtwts):
                lmranks[i].append(ranke(lms[i], item['lm']))
                tmranks[i].append(ranke(tms[i], item['tm']))
            wmranks.append(ranke(wms, item['lm']))
            randranks.append(randranke(city))

    for i in range(len(numtwts)):
        for ranklm, ranktm in zip(lmranks[i], tmranks[i]):
            lmtmranks[i].append(linearjoin([ranklm, ranktm], [0.5, 0.5]))
        for ranklm, rankwm in zip(lmranks[i], wmranks):
            wmlmranks[i].append(linearjoin([ranklm, rankwm], [0.5, 0.5]))
        for ranklm, ranktm, rankwm in zip(lmranks[i], tmranks[i], wmranks):
            wmlmtmranks[i].append(\
                    linearjoin([ranklm, ranktm, rankwm], [0.33, 0.33, 0.33]))

    # plot
    candls = ['-', '--', '-.']
    # mks = ['o', '^', '*']

    #for i in range(len(numtwts)):
        #lmeval = batcheval(lmranks[i], test['label'])
        #plt.plot(lmeval['pos'], lmeval['rate'],
                #label='tweet(s={0})'.format(numtwts[i]),
                #ls=candls[i%2], marker=mks[i/2])
    #for i in range(len(numtwts)):
        #for plc in placetotalrank(lmranks[i], test)['label'][-10:]:
            #print place_name(plc), plc
        #print placetotalrank(lmranks[i], test)['totalrank'][-10:]
        #print wilcoxontest(lmranks[i], lmranks[i-1], test)
    #plt.legend(loc='lower right')
#---------------------------------------------------------------
    for i in range(len(numtwts)):
        lmeval = batcheval(lmranks[i], test['label'])
        plt.plot(lmeval['pos'], lmeval['rate'],
                 label='tweet(s={0})'.format(numtwts[i]),
                 ls=candls[i], marker='o')
        # wmlmeval = batcheval(wmlmranks[i], test['label'])
        # plt.plot(wmlmeval['pos'], wmlmeval['rate'],
        #          label='tweet(s={0})+web'.format(numtwts[i]),
        #          ls=candls[i], marker='^')
        # print 'Wilcoxon (lm vs wmlm):', wilcoxontest(lmranks[i], wmlmranks[i], test)
        # print 'Place id -> name:'
        # for plc in placetotalrank(wmlmranks[i], test)['label'][-10:]:
        #     print place_name(plc), plc
        # print 'Place Total Rank:'
        # print placetotalrank(wmlmranks[i], test)['totalrank'][-10:]
    # wmeval = batcheval(wmranks, test['label'])
    # print 'Place id -> name:'
    # for plc in placetotalrank(wmranks, test)['label'][-10:]:
    #     print place_name(plc), plc
    # print 'Place Total Rank'
    # print placetotalrank(wmranks, test)['totalrank'][-10:]
    # plt.plot(wmeval['pos'], wmeval['rate'],
    #          label='web',
    #          ls=':')
#---------------------------------------------------------------


    #for i in range(len(numtwts)):
        #plt.subplot(121 + i)
        #plt.title('$s={0}$'.format(numtwts[i]))
        #lmeval = batcheval(lmranks[i], test['label'])
        #plt.plot(lmeval['pos'], lmeval['rate'],
                #label='tweet',
                #ls=candls[i], marker='o')
        #lmtmeval = batcheval(lmtmranks[i], test['label'])
        #plt.plot(lmtmeval['pos'], lmtmeval['rate'],
                #label='tweet+time',
                #ls=candls[i], marker='^')
        #wmlmtmeval = batcheval(wmlmtmranks[i], test['label'])
        #plt.plot(wmlmtmeval['pos'], wmlmtmeval['rate'],
                #label='tweet+time+web',
                #ls=candls[i], marker='*')
        #plt.legend(loc='lower right')
        #plt.ylabel('Rate containing Reference POI')
        #plt.xlabel('Top $p$ places')
    #plt.show()
#---------------------------------------------------------------
    #i=0
    #plt.subplot(121 + i)
    #plt.title('$s={0}$'.format(numtwts[i]))
    #tmeval = batcheval(tmranks[i], test['label'])
    #plt.plot(tmeval['pos'], tmeval['rate'],
            #label='time',
            #ls=candls[i], marker='o')
    #lmeval = batcheval(lmranks[i], test['label'])
    #plt.plot(lmeval['pos'], lmeval['rate'],
            #label='tweet',
            #ls=candls[i], marker='^')
    #lmtmeval = batcheval(lmtmranks[i], test['label'])
    #plt.plot(lmtmeval['pos'], lmtmeval['rate'],
            #label='tweet+time',
            #ls=candls[i], marker='*')
    #for plc in placetotalrank(tmranks[i], test)['label'][-10:]:
        #print place_name(plc), plc
    #print placetotalrank(tmranks[i], test)['totalrank'][-10:]
    #for plc in placetotalrank(lmtmranks[i], test)['label'][-10:]:
        #print place_name(plc), plc
    #print placetotalrank(lmtmranks[i], test)['totalrank'][-10:]
    #print wilcoxontest(lmranks[i], lmtmranks[i], test)

    #plt.legend(loc='lower right')
    #plt.ylabel('Rate containing Reference POI')
    #plt.xlabel('Top $p$ places')


    #i=1
    #plt.subplot(121 + i)
    #plt.title('$s={0}$'.format(numtwts[i]))
    #tmeval = batcheval(tmranks[i], test['label'])
    #plt.plot(tmeval['pos'], tmeval['rate'],
            #label='time',
            #ls=candls[i], marker='o')
    #wmlmeval = batcheval(wmlmranks[i], test['label'])
    #plt.plot(wmlmeval['pos'], wmlmeval['rate'],
            #label='tweet + web',
            #ls=candls[i], marker='^')
    #wmlmtmeval = batcheval(wmlmtmranks[i], test['label'])
    #plt.plot(wmlmtmeval['pos'], wmlmtmeval['rate'],
            #label='tweet+time+web',
            #ls=candls[i], marker='*')

    #for plc in placetotalrank(wmlmranks[i], test)['label'][-10:]:
        #print place_name(plc), plc
    #print placetotalrank(wmlmranks[i], test)['totalrank'][-10:]
    #for plc in placetotalrank(wmlmtmranks[i], test)['label'][-10:]:
        #print place_name(plc), plc
    #print placetotalrank(wmlmtmranks[i], test)['totalrank'][-10:]
    #print wilcoxontest(wmlmranks[i], wmlmtmranks[i], test)

    #plt.legend(loc='lower right')
    #plt.ylabel('Rate containing Reference POI')
    #plt.xlabel('Top $p$ places')

    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.show()

def richrank(cities, names):
    candls = ['-', '--', '.-']
    mks = ['o', '^', '*', 'v', 's']
    for idx in range(len(cities)):
        lms = dict()
        test = Dataset()
        for pid in cities[idx]:
            twtp = loadrows(GEOTWEET, ('place_id', 'text', 'created_at'),
                            ('place_id=\'{0}\''.format(pid),), 'sample_switch_place_cate',
                            'order by rand() limit 110')
            lms[pid] = LanguageModel(twtp['text'][:100])
            for cnt in range(100, 110):
                test.append({'label': twtp['place_id'][cnt],
                             'lm': LanguageModel([twtp['text'][cnt],])})

        lmranks = list()
        for twtlm in test:
            lmranks.append(ranke(lms, twtlm['lm']))

        lmeval = batcheval(lmranks, test['label'])
        plt.plot(lmeval['pos'], lmeval['rate'], ls=candls[idx%2], marker=mks[idx/2],
                 label='{0}($s=100$)'.format(names[idx]))
    plt.legend(loc='lower right')
    plt.ylabel('Rate containing referece POI')
    plt.xlabel('Top $p$ places')
    plt.show()

def cntdist():
    """docstring for cntdist
    """
    with open('cntdist.csv') as fin:
        cnts = [int(cnt.strip()) for cnt in fin]
        plt.loglog(range(len(cnts)), cnts)
        plt.xlabel('POIs ordered by # of tweets')
        plt.ylabel('# of tweets')
        plt.show()


def run():
    """ Test this module
    """
    cities = list()
    for city in ['ch10_cate.lst', 'la10_cate.lst', 'ny10_cate.lst', 'sf10_cate.lst']:
        with open('data/' + city) as fin:
            cities.append([p.strip() for p in fin])
    #cmptimeweb(cities, [100, 25, 10, 5], 10)
    cmptimeweb(cities, [1000, 100, 5], 10)
    #richrank(cities, ['Chicago', 'Los Angeles', 'New York', 'San Francisco'])

if __name__ == '__main__':
    run()
