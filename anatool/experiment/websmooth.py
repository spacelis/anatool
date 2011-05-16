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
def webmodel(place_id):
    """ Build language models from web pages searched by query the place name
        @arg place_id the place ID in Twitter system
        @return LM made from the web pages
    """
    cur = CONN_POOL.get_cur(GEOTWEET)
    cur.execute('select web from web where place_id = \'{0}\''.format(place_id))
    text_web = [row['web'] for row in cur]
    return lmfromtext(text_web)

@Cache()
def twtmodel(place_id):
    """ Build language models from tweets located at place_id
        @arg place_id the place ID in Twitter system
        @return LM made from the web pages
    """
    cur = CONN_POOL.get_cur(GEOTWEET)
    cur.execute('select text from sample' \
            ' where place_id = \'{0}\' limit {1}'.format(place_id, randint(5,20)))
    text_web = [row['text'] for row in cur]
    return lmfromtext(text_web)

def guess(text, candidates, method):
    """ Guess where the text from. Rank the place by comparing the difference
        between the LM provided by method of the places and the LM from the text
        @arg text the testing text, list() of str()
        @arg candidates the candidates of places, list() of place IDs
        @return an ordered Dataset() of {'pid', 'kld'}
    """
    lmweb = dict()
    for place_id in candidates:
        place_id = place_id.strip()
        lmweb[place_id] = method(place_id)
    lmtest = lmfromtext(text)
    rank = list()
    for pid_web in lmweb.iterkeys():
        rank.append((pid_web, kl_divergence(lmweb[pid_web], lmtest)))
    rank = sorted(rank, key=itemgetter(1), reverse=False)
    res = Dataset()
    for item in rank:
        res.append({'pid': item[0], 'kld': item[1]})
    return res

def joinedguess(text, candidates, lmd):
    """ Join the two language model to generate more accurate results
    """
    twtges = guess(text, candidates, twtmodel)
    webges = guess(text, candidates, webmodel)
    twtges['kld'] = reunit(twtges['kld'])
    webges['kld'] = reunit(webges['kld'])
    rank = list()
    for titem, witem in zip(twtges.sorted_items('pid'), webges.sorted_items('pid')):
        if titem['pid'] == witem['pid']:
            rank.append((titem['pid'],
                lmd * titem['kld'] + (1 - lmd) * witem['kld']))
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

def batcheval(expects, maxpos, rankslst, labels):
    """ The batch version of evaluate() which test a set of pos
        @arg ranks list() of ranks returned by webguess()
        @arg expects list() of expected place_ids
        @arg maxpos the max position
        @return a list of rates of goals
    """
    for ranks, lbl in zip(rankslst, labels):
        goalrates = Dataset()
        for pos in range(maxpos + 1):
            goalrates.append({'pos': pos, 'rate': evaluate(ranks, expects, pos)})
        print goalrates['rate']
        plt.plot(range(maxpos + 1), goalrates['rate'], label=lbl)
    plt.xlabel('List Length')
    plt.ylabel('Goal Rate')
    plt.title('Goal Graph')
    plt.legend(loc='lower right')
    plt.show()

#--------------------------------------------------------------- setups

def setup(places, num):
    """ This setup considers the tweets from the places in the list and select
        some number of tweets from those places as testing tweets
        @arg city the place_id of the city
        @arg num the number of tweets generated
        @return a list() of tuple (text, cadidates)
    """
    twt = Dataset()
    for pid in places:
        twt.extend(loadrows(GEOTWEET, ('place_id', 'text', 'created_at'),
                ('place_id=\'{0}\''.format(pid),), 'sample',
                'order by rand() limit {0}'.format(num/len(places) + 1)))
    joinedranks = list()
    for item in twt:
        joinedranks.append(joinedguess([item['text'],], places, 0.6))
    webranks = list()
    for item in twt:
        webranks.append(guess([item['text'],], places, webmodel))
    twtranks = list()
    for item in twt:
        twtranks.append(guess([item['text'],], places, twtmodel))
    batcheval(twt['place_id'], len(places),
            [joinedranks, webranks, twtranks],
            ['joined', 'web', 'tweet']
            )

def test():
    """ execute the setups
    """
    with open('newyork10.lst') as fin:
        setup([p.strip() for p in fin], 100) #New York City
    #evaluate2(web_based_guess2())
    pass


if __name__ == '__main__':
    test()

