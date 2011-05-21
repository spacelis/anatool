#!python
# -*- coding: utf-8 -*-
"""File: websmooth.py
Description:
    Verifying whether the web pages from search engine can support tweets
    smoothing in place wise.
History:
    0.2.0 add ranking place by web pages
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import matplotlib.pyplot as plt
from random import randint
from operator import itemgetter
from anatool.dm.db import CONN_POOL, GEOTWEET
from anatool.analyze.dataset import Dataset, place_name, loadrows
from anatool.analyze.lm import lmfromtext, kl_divergence
from anatool.experiment.evaluation import evaluate, batcheval
from annotation import Cache

#--------------------------------------------------------------- Tool


#--------------------------------------------------------------- setups

def linestyles(styles=['-', '--', '-.', ':']):
    """ Yield different styles in iteration
    """
    while True:
        for style in styles:
            yield style

def kldiff(places):
    """ compare the difference of kl-divergence between tweets and web pages
        for each place in places
    """
    diff = Dataset()
    for pid in places:
        twt = loadrows(GEOTWEET, ('place_id', 'text'),
                ('place_id=\'{0}\''.format(pid),), 'sample',
                'order by rand() limit {0}'.format(100))
        web = loadrows(GEOTWEET, ('place_id', 'web'),
                ('place_id=\'{0}\''.format(pid),), 'web',
                'limit 25')
        lmref = lmfromtext(twt['text'][:50])
        lmtwt = lmfromtext(twt['text'][51:])
        lmweb = lmfromtext(web['web'])
        diff.append({'pid': pid, 'twtkld': kl_divergence(lmtwt, lmref),
            'webkld': kl_divergence(lmweb, lmref)})
    for item in diff:
        print '{0} & {1} & {2}'.format(place_name(item['pid']), item['twtkld'], item['webkld'])

def onesetup(places, numtwts, numtest, balance):
    """ This setup considers the tweets from the places in the list and select
        some number of tweets from those places as testing tweets, the query is just one tweet
        @arg city the place_id of the city
        @arg num the number of tweets generated
        @return a list() of tuple (text, cadidates)
    """
    lsts = linestyles()
    # prepare for data
    twtmodel = dict()
    webmodel = dict()
    twttest = Dataset()
    for pid in places:
        twtp = loadrows(GEOTWEET, ('place_id', 'text'),
                ('place_id=\'{0}\''.format(pid),), 'sample',
                'order by rand() limit {0}'.format(max(numtwts) + numtest))
        webmodel[pid] = loadrows(GEOTWEET, ('place_id', 'web'),
                ('place_id=\'{0}\''.format(pid),), 'web',
                'order by rand() limit 30')['web']
        twtmodel[pid] = twtp['text'][:max(numtwts)]
        for idx in range(max(numtwts) + 1, twtp.size()):
            twttest.append(twtp.item(idx))

    # ranking by twt and twt+web
    for numtwt in numtwts:
        lmtwt = dict()
        lmweb = dict()
        for pid in twtmodel.iterkeys():
            lmtwt[pid] = lmfromtext(twtmodel[pid][:numtwt])
            lmweb[pid] = lmfromtext(webmodel[pid])
        jointranks = list()
        for item in twttest:
            jointranks.append(joint_ranking(lmfromtext([item['text'],]), lmtwt, lmweb, balance))
        twtranks = list()
        for item in twttest:
            twtranks.append(kl_ranking(lmtwt, lmfromtext([item['text'],])))
        gjoint = batcheval(twttest['place_id'], len(places), jointranks)
        gtwt = batcheval(twttest['place_id'], len(places), twtranks)
        plt.plot(gjoint['pos'], gjoint['rate'], marker='^',
                label='JOINT($t={0}$)'.format(numtwt), linestyle=lsts.next())
        plt.plot(gtwt['pos'], gtwt['rate'], marker='o',
                label='TWEET($t={0}$)'.format(numtwt), linestyle=lsts.next())

    webranks = list()
    for item in twttest:
        webranks.append(kl_ranking(lmweb, lmfromtext([item['text'],])))
    gweb = batcheval(twttest['place_id'], len(places), webranks)
    plt.plot(gweb['pos'], gweb['rate'], label='WEB', linestyle='dotted')
    plt.xlabel('First $n$ Places')
    plt.ylabel('Probability')
    plt.legend(loc='lower right')
    plt.show()

def sparsitysetup(nums):
    """ This setup considers the tweets from the places in the list and select
        some number of tweets from those places as testing tweets, the query is a block of tweets
        @arg city the place_id of the city
        @arg num the number of tweets generated
        @return a list() of tuple (text, cadidates)
    """
    lsts = linestyles()
    for num in nums:
        with open('chicago10.lst') as fin:
            twt = Dataset()
            places = [p.strip() for p in fin]
            lmplc = dict()
            lmtwt = Dataset()
            for pid in places:
                cur = CONN_POOL.get_cur(GEOTWEET)
                cur.execute('select text from sample' \
                        ' where place_id = \'{0}\' order by rand() limit {1}'.format(pid, 160))
                text = [row['text'] for row in cur]
                lmplc[pid] = lmfromtext(text[:num])
                for txt in text[150:160]:
                    lmtwt.append({'pid': pid, 'lm': lmfromtext([txt,])})
            ranks = list()
            for item in lmtwt:
                ranks.append(kl_ranking(lmplc, item['lm']))
            gch = batcheval(lmtwt['pid'], len(places), ranks)
            plt.plot(gch['pos'], gch['rate'],
                    lsts.next(), label='t={0}'.format(num))
    plt.xlabel('First $n$ places')
    plt.ylabel('Probability')
    plt.legend(loc='lower right')
    plt.show()

def test():
    """ execute the setups
    """
    with open('chicago10_web.lst') as fin:
        onesetup([p.strip() for p in fin], [100, 5], 10, 0.5) #New York City
    #sparsitysetup([100, 25, 10, 5])
    #with open('chicago10.lst') as fin:
        #kldiff([p.strip() for p in fin]) #New York City


if __name__ == '__main__':
    test()

