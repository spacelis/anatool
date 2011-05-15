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

import csv
import matplotlib.pyplot as plt
from operator import itemgetter
from anatool.dm.db import CONN_POOL, GEOTWEET
from anatool.analyze.dataset import Dataset, place_name, loadrows
from anatool.analyze.lm import lmfromtext, kl_divergence
from annotation import Cache

#--------------------------------------------------------------- Experiment
@Cache()
def webmodel(place_id):
    """ Build language models for place_id from webs
        @arg place_id the place ID in Twitter system
        @return LM made from the web pages
    """
    #FIXME untest
    cur = CONN_POOL.get_cur(GEOTWEET)
    cur.execute('select web from web where place_id = \'{0}\''.format(place_id))
    text_web = [row['web'] for row in cur]
    return lmfromtext(text_web)

def webguess(text, candidates):
    """ Guess where the text from. Rank the place by comparing the difference
        between the LM from web pages of the places and the LM from the tweets
        @arg text the testing text, list() of str()
        @arg candidates the candidates of places, list() of place IDs
        @return an ordered Dataset() of {'pid', 'kld'}
    """
    #FIXME untest
    lmweb = dict()
    for place_id in candidates:
        place_id = place_id.strip()
        lmweb[place_id] = webmodel(place_id)
    lmtxt = lmfromtext(text)
    rank = list()
    for pid_web in lmweb.iterkeys():
        rank.append((pid_web, kl_divergence(lmweb[pid_web], lmtxt)))
    rank = sorted(rank, key=itemgetter(1), reverse=False)
    res = Dataset()
    for item in rank:
        res.append({'pid': item[0], 'kld': item[1]})
    print text
    print res
    return res

def tweetguess():
    #TODO guess only by tweet lm
    pass

def evaluate(ranks, expects, pos):
    """ Evaluate the ranking algorithms seeing the expected place_id in the
        rank higher than given pos
        @arg ranks list() of ranks returned by webguess()
        @arg expects list() of expected place_ids
        @arg pos the given position seen as length of system returned
        @return the rate of goals
    """
    #FIXME untest
    goal = 0
    for expr in range(len(ranks)):
        if expects[expr] in set(ranks[expr]['pid'][:pos]):
            goal += 1
    return float(goal) / len(ranks)

def batcheval(ranks, expects, maxpos):
    """ The batch version of evaluate() which test a set of pos
        @arg ranks list() of ranks returned by webguess()
        @arg expects list() of expected place_ids
        @arg maxpos the max position
        @return a list of rates of goals
    """
    goalrates = Dataset()
    for pos in range(maxpos + 1):
        goalrates.append({'pos': pos, 'rate': evaluate(ranks, expects, pos)})
    print goalrates['rate']
    plt.plot(range(maxpos + 1), goalrates['rate'], 'k')
    plt.xlabel('List Length')
    plt.ylabel('Goal Rate')
    plt.title('Goal Graph')
    plt.show()

#--------------------------------------------------------------- experiment setups

def setup(places, num):
    """ This setup considers the tweets from the places in the list and select
        some number of tweets from those places as testing tweets
        @arg city the place_id of the city
        @arg num the number of tweets generated
        @return a list() of tuple (text, cadidates)
    """
    cur = CONN_POOL.get_cur(GEOTWEET)
    twt = Dataset()
    for pid in places:
        twt.extend(loadrows(GEOTWEET, ('place_id', 'text', 'created_at'), \
                ('place_id=\'{0}\''.format(pid),), 'sample', 'order by rand() limit {0}'.format(num/len(places) + 1)))
    ranks = list()
    for item in twt:
        ranks.append(webguess([item['text'],], places))
    batcheval(ranks, twt['place_id'], len(places))

#TODO add a function to make an experiment
def expr():
    with open('newyork10.lst') as fin:
        setup([p.strip() for p in fin], 100) #New York City
    #evaluate2(web_based_guess2())


if __name__ == '__main__':
    expr()

