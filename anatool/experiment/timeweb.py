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
    lmranks = [list() for i in range(len(numtwts))]
    tmranks = [list() for i in range(len(numtwts))]
    wmranks = list()
    randranks = list()
    lmtmranks = [list() for i in range(len(numtwts))]
    wmlmranks = [list() for i in range(len(numtwts))]
    wmlmtmranks = [list() for i in range(len(numtwts))]
    test = Dataset()

    for places in cities:
        lms = [dict() for i in range(len(numtwts))]
        tms = [dict() for i in range(len(numtwts))]
        wms = dict()
        tst = Dataset()
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
            for i in range(max(numtwts), max(numtwts) + numtest):
                tst.append({'label': pid,
                    'lm': LanguageModel([twtp['text'][i],]),
                    'tm': TimeModel([twtp['created_at'][i],])})

        test.extend(tst)
        # rank
        for item in tst:
            for i in range(len(numtwts)):
                lmranks[i].append(ranke(lms[i], item['lm']))
                tmranks[i].append(ranke(tms[i], item['tm']))
            wmranks.append(ranke(wms, item['lm']))
            randranks.append(randranke(places))

    for i in range(len(numtwts)):
        for ranklm, ranktm in zip(lmranks[i], tmranks[i]):
            lmtmranks[i].append(linearjoin([ranklm, ranktm], [0.5, 0.5]))
        for ranklm, rankwm in zip(lmranks[i], wmranks):
            wmlmranks[i].append(linearjoin([ranklm, rankwm], [0.5, 0.5]))
        for ranklm, ranktm, rankwm in zip(lmranks[i], tmranks[i], wmranks):
            wmlmtmranks[i].append(\
                    linearjoin([ranklm, ranktm, rankwm], [0.33, 0.33, 0.33]))

    # plot
    candls = ['-', '--']
    mks = ['o', '^', '*', 'v', 's']

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
        wmlmeval = batcheval(wmlmranks[i], test['label'])
        plt.plot(wmlmeval['pos'], wmlmeval['rate'],
                label='tweet(s={0})+web'.format(numtwts[i]),
                ls=candls[i], marker='^')
        print wilcoxontest(lmranks[i], wmlmranks[i], test)
        for plc in placetotalrank(wmlmranks[i], test)['label'][-10:]:
            print place_name(plc), plc
        print placetotalrank(wmlmranks[i], test)['totalrank'][-10:]
    wmeval = batcheval(wmranks, test['label'])
    for plc in placetotalrank(wmranks, test)['label'][-10:]:
        print place_name(plc), plc
    print placetotalrank(wmranks, test)['totalrank'][-10:]
    plt.plot(wmeval['pos'], wmeval['rate'],
            label='web',
            ls=':')

    plt.plot(lmeval['pos'], [float(r) / max(lmeval['pos']) for r in lmeval['pos']],
             ls='-.', marker='s',
             label='Random Baseline')
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

    plt.legend(loc='lower right')
    plt.ylabel('Rate containing Reference POI')
    plt.xlabel('Top $p$ places')

    plt.show()


def cmpsparsecombine(cities, numtwts, numtest):
    """ the combined model performance under the influence of sparseness
    """
    lmranks = [list() for i in range(len(numtwts))]
    tmranks = [list() for i in range(len(numtwts))]
    wmranks = list()
    randranks = list()
    lmtmranks = [list() for i in range(len(numtwts))]
    wmlmranks = [list() for i in range(len(numtwts))]
    wmlmtmranks = [list() for i in range(len(numtwts))]
    test = Dataset()

    for places in cities:
        lms = [dict() for i in range(len(numtwts))]
        tms = [dict() for i in range(len(numtwts))]
        wms = dict()
        tst = Dataset()
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
            for i in range(max(numtwts), max(numtwts) + numtest):
                tst.append({'label': pid,
                            'lm': LanguageModel([twtp['text'][i],]),
                            'tm': TimeModel([twtp['created_at'][i],])})

        test.extend(tst)
        # rank
        for item in tst:
            for i in range(len(numtwts)):
                lmranks[i].append(ranke(lms[i], item['lm']))
                tmranks[i].append(ranke(tms[i], item['tm']))
            wmranks.append(ranke(wms, item['lm']))
            randranks.append(randranke(places))

    for i in range(len(numtwts)):
        for ranklm, ranktm in zip(lmranks[i], tmranks[i]):
            lmtmranks[i].append(linearjoin([ranklm, ranktm], [0.5, 0.5]))
        for ranklm, rankwm in zip(lmranks[i], wmranks):
            wmlmranks[i].append(linearjoin([ranklm, rankwm], [0.5, 0.5]))
        for ranklm, ranktm, rankwm in zip(lmranks[i], tmranks[i], wmranks):
            wmlmtmranks[i].append(\
                    linearjoin([ranklm, ranktm, rankwm], [0.33, 0.33, 0.33]))

    # plot
    candls = ['-', '--']
    mks = ['o', '^', '*', 'v', 's']

    i=0
    plt.subplot(121 + i)
    plt.title('$s={0}$'.format(numtwts[i]))
    tmeval = batcheval(tmranks[i], test['label'])
    plt.plot(tmeval['pos'], tmeval['rate'],
            label='time',
            ls=candls[i], marker='o')
    lmeval = batcheval(lmranks[i], test['label'])
    plt.plot(lmeval['pos'], lmeval['rate'],
            label='tweet',
            ls=candls[i], marker='^')
    lmtmeval = batcheval(lmtmranks[i], test['label'])
    plt.plot(lmtmeval['pos'], lmtmeval['rate'],
            label='tweet+time',
            ls=candls[i], marker='*')
    for plc in placetotalrank(tmranks[i], test)['label'][-10:]:
        print place_name(plc), plc
    print placetotalrank(tmranks[i], test)['totalrank'][-10:]
    for plc in placetotalrank(lmtmranks[i], test)['label'][-10:]:
        print place_name(plc), plc
    print placetotalrank(lmtmranks[i], test)['totalrank'][-10:]
    print wilcoxontest(lmranks[i], lmtmranks[i], test)

    plt.plot(lmeval['pos'], [float(r) / max(lmeval['pos']) for r in lmeval['pos']],
             ls='-.', marker='s',
             label='Random Baseline')
    plt.legend(loc='lower right')
    plt.ylabel('Rate containing Reference POI')
    plt.xlabel('Top $p$ places')


    i=1
    plt.subplot(121 + i)
    plt.title('$s={0}$'.format(numtwts[i]))
    tmeval = batcheval(tmranks[i], test['label'])
    plt.plot(tmeval['pos'], tmeval['rate'],
            label='time',
            ls=candls[i], marker='o')
    wmlmeval = batcheval(wmlmranks[i], test['label'])
    plt.plot(wmlmeval['pos'], wmlmeval['rate'],
            label='tweet + web',
            ls=candls[i], marker='^')
    wmlmtmeval = batcheval(wmlmtmranks[i], test['label'])
    plt.plot(wmlmtmeval['pos'], wmlmtmeval['rate'],
            label='tweet+time+web',
            ls=candls[i], marker='*')

    for plc in placetotalrank(wmlmranks[i], test)['label'][-10:]:
        print place_name(plc), plc
    print placetotalrank(wmlmranks[i], test)['totalrank'][-10:]
    for plc in placetotalrank(wmlmtmranks[i], test)['label'][-10:]:
        print place_name(plc), plc
    print placetotalrank(wmlmtmranks[i], test)['totalrank'][-10:]
    print wilcoxontest(wmlmranks[i], wmlmtmranks[i], test)

    plt.plot(lmeval['pos'], [float(r) / max(lmeval['pos']) for r in lmeval['pos']],
             ls='-.', marker='s',
             label='Random Baseline')
    plt.legend(loc='lower right')
    plt.ylabel('Rate containing Reference POI')
    plt.xlabel('Top $p$ places')

    plt.show()


def cmpsparse(cities, numtwts, numtest):
    """ Compare the model performance trained with different amount of tweets
    """
    lmranks = [list() for i in range(len(numtwts))]
    randranks = list()
    lmtmranks = [list() for i in range(len(numtwts))]
    test = Dataset()

    for places in cities:
        lms = [dict() for i in range(len(numtwts))]
        tst = Dataset()
        for pid in places:
            twtp = loadrows(GEOTWEET, ('place_id', 'text', 'created_at'),
                    ('place_id=\'{0}\''.format(pid),), 'sample',
                    'order by rand() limit {0}'.format(max(numtwts) + numtest))
            for i in range(len(numtwts)):
                lms[i][pid] = LanguageModel(twtp['text'][:numtwts[i]])

            # test data
            for i in range(max(numtwts), max(numtwts) + numtest):
                tst.append({'label': pid,
                            'lm': LanguageModel([twtp['text'][i],]),
                            })

        test.extend(tst)
        # rank
        for item in tst:
            for i in range(len(numtwts)):
                lmranks[i].append(ranke(lms[i], item['lm']))
            randranks.append(randranke(places))

    # plot
    candls = ['-', '--']
    mks = ['o', '^', '*', 'v', 's']

    for i, n in enumerate(numtwts):
        lmeval = batcheval(lmranks[i], test['label'])
        plt.plot(lmeval['pos'], lmeval['rate'],
                label='tweet(s={0})'.format(n),
                marker=mks[i])

    plt.plot(lmeval['pos'], [float(r) / max(lmeval['pos']) for r in lmeval['pos']],
             ls='-.', marker='s',
             label='Random Baseline')
    plt.legend(loc='lower right')
    plt.ylabel('Rate containing Reference POI')
    plt.xlabel('Top $p$ places')

    plt.show()


def richrank(cities, names):
    candls = ['-', '--']
    mks = ['o', '^', '*']
    for idx in range(len(cities)):
        lms = dict()
        test = Dataset()
        for pid in cities[idx]:
            twtp = loadrows(GEOTWEET, ('place_id', 'text', 'created_at'),
                    ('place_id=\'{0}\''.format(pid),), 'sample',
                    'order by rand() limit 110')
            lms[pid] = LanguageModel(twtp['text'][:100])
            for cnt in range(100, 110):
                test.append({'label': twtp['place_id'][cnt],
                            'lm': LanguageModel([twtp['text'][cnt],])})

        lmranks = list()
        randranks = list()
        for twtlm in test:
            lmranks.append(ranke(lms, twtlm['lm']))
            randranks.append(randranke(cities[idx]))

        lmeval = batcheval(lmranks, test['label'])
        print names[idx], 'P@1', (lmeval['rate'][1] - 0.1)
        plt.plot(lmeval['pos'], lmeval['rate'], ls=candls[idx%2], marker=mks[idx/2],
                label='{0}($s=100$)'.format(names[idx]))
    plt.plot(lmeval['pos'], [float(r) / max(lmeval['pos']) for r in lmeval['pos']],
             ls='-.', marker='s',
             label='Random Baseline')
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
    for city in ['ch10_web.lst', 'la10_web.lst', 'ny10_web.lst', 'sf10_web.lst']:
        with open('data/' + city) as fin:
            cities.append([p.strip() for p in fin])
    # cmpsparse(cities, [100, 25, 10, 5], 10)
    # cmpsparsecombine(cities, [100, 5], 10)
    cmptimeweb(cities, [100, 5], 10)
    # richrank(cities, ['Chicago', 'Los Angeles', 'New York', 'San Francisco'])

if __name__ == '__main__':
    run()
