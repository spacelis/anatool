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
from annotation import Cache

#--------------------------------------------------------------- Tool

def reunit(vector):
    """ Map all values in vector into [0, 1]
        a^'_i = (a_i - m) / n where m is the min(vector), n = max(vector) -
        min(vecotr)
        @arg vector a list() of numbers
        @return a list() of numbers reunited
    """
    vecmin = min(vector)
    vecmax = max(vector)
    return [float(val - vecmin) / (vecmax - vecmin) for val in vector]

#--------------------------------------------------------------- Experiment

@Cache()
def webmodel(place_id, cnt):
    """ Build language models from web pages searched by query the place name
        @arg place_id the place ID in Twitter system
        @return LM made from the web pages
    """
    cur = CONN_POOL.get_cur(GEOTWEET)
    cur.execute('select web from web where '\
            'place_id = \'{0}\' limit {1}'.format(place_id, cnt))
    text_web = [row['web'] for row in cur]
    return lmfromtext(text_web)

@Cache()
def twtmodel(place_id, cnt):
    """ Build language models from tweets located at place_id
        @arg place_id the place ID in Twitter system
        @return LM made from the web pages
    """
    cur = CONN_POOL.get_cur(GEOTWEET)
    cur.execute('select text from sample' \
            ' where place_id = \'{0}\' limit {1}'.format(place_id, cnt))
    text_web = [row['text'] for row in cur]
    return lmfromtext(text_web)

def kl_ranking(lmcand, lmtext):
    """ Rank the LM in lmcand according to the KL-divergences to LM from text
        @arg text list() of str()
        @arg lmcand dict() of place_id to lm
        @return an ordered Dataset() of {'pid', 'kld'}
    """
    rank = list()
    for pid in lmcand.iterkeys():
        rank.append((pid, kl_divergence(lmcand[pid], lmtext)))
    rank = sorted(rank, key=itemgetter(1), reverse=False)
    res = Dataset()
    for item in rank:
        res.append({'pid': item[0], 'kld': item[1]})
    return res

def guess(text, candidates, method):
    """ Guess where the text from. Rank the place by comparing the difference
        between the LM provided by method of the places and the LM from the text
        @arg text the testing text, list() of str()
        @arg candidates the candidates of places, list() of place IDs
        @return an ordered Dataset() of {'pid', 'kld'}
    """
    lmcand = dict()
    for place_id in candidates:
        place_id = place_id.strip()
        lmcand[place_id] = method(place_id, 1000)
    return kl_ranking(lmfromtext(text), lmcand)

def joint_ranking(lmtest, lmtwt, lmweb, balance):
    """ Join the two language model to generate more accurate results
    """
    twtges = kl_ranking(lmtwt, lmtest)
    webges = kl_ranking(lmweb, lmtest)
    twtges['kld'] = reunit(twtges['kld'])
    webges['kld'] = reunit(webges['kld'])
    rank = list()
    for titem, witem in zip(twtges.sorted_items('pid'), webges.sorted_items('pid')):
        if titem['pid'] == witem['pid']:
            rank.append((titem['pid'],
                balance * titem['kld'] + (1 - balance) * witem['kld']))
    rank = sorted(rank, key=itemgetter(1), reverse=False)
    res = Dataset()
    for item in rank:
        res.append({'pid': item[0], 'kld': item[1]})
    return res

def evaluate(ranks, expects, pos):
    """ Evaluate the ranking algorithms seeing the expected place_id in the
        rank higher than given pos
        @arg ranks list() of ranks returned by webguess()
        @arg expects list() of expected place_ids
        @arg pos the given position seen as length of system returned
        @return the rate of goals
    """
    goal = 0
    for expr in range(len(ranks)):
        if expects[expr] in set(ranks[expr]['pid'][:pos]):
            goal += 1
    return float(goal) / len(ranks)

def batcheval(expects, maxpos, ranks):
    """ The batch version of evaluate() which test a set of pos
        @arg ranks list() of ranks returned by webguess()
        @arg expects list() of expected place_ids
        @arg maxpos the max position
        @return a list of rates of goals
    """
    goalrates = Dataset()
    for pos in range(maxpos + 1):
        goalrates.append({'pos': pos, 'rate': evaluate(ranks, expects, pos)})
    return goalrates


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

