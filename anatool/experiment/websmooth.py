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
from anatool.dm.db import CONN_POOL, GEOTWEET
from anatool.analyze.dataset import Dataset, place_name
from anatool.analyze.lm import lmfromtext, kl_divergence
from operator import itemgetter

def lm_comp():
    """ This function compares between the LMs from web pages and tweets hot places.
    """
    cur = CONN_POOL.get_cur(GEOTWEET)
    cwr = csv.writer(open('kld.csv', 'wb'), delimiter=';',
            quotechar='"')

    fin = open('../../data/web.csv')
    cwr.writerow(['place_name', 'KL(lmweb, lmref)', '#Terms(lmweb)',
        'KL(lmtwt, lmref)', '#Terms(lmtwt)', '#Terms(lmref)'])
    for line in fin:
        line = line.strip()
        cur.execute('select web from web where place_id = \'{0}\''.format(line))
        text_web = [row['web'] for row in cur]
        lmweb = lmfromtext(text_web)

        cur.execute('select text from sample where place_id = \'{0}\' order by rand()'.format(line))
        twt = [row['text'] for row in cur]
        # First half of the tweets are used as references
        text_ref = twt[0:len(twt)/2]
        lmref = lmfromtext(text_ref)
        # Second half of the tweets are used as counter-parts
        text_twt = twt[len(twt)/2 + 1:]
        lmtwt = lmfromtext(text_twt)
        print place_name(line, GEOTWEET), kl_divergence(lmweb, lmref), kl_divergence(lmtwt, lmref)
        cwr.writerow([place_name(line, GEOTWEET), kl_divergence(lmweb, lmref), len(lmweb),
            kl_divergence(lmtwt, lmref), len(lmtwt), len(lmtwt)])

def web_based_guess():
    """This experiment rank the place by comparing LM from webs to LM from tweets
    """
    cur = CONN_POOL.get_cur(GEOTWEET)
    fin = open('../../data/list/sample_dist_100.csv')

    #load text and build LM for both tweets and web pages
    lmweb = dict()
    lmtwt = dict()
    for place_id in fin:
        place_id = place_id.strip()
        cur.execute('select web from web where place_id = \'{0}\''.format(place_id))
        text_web = [row['web'] for row in cur]
        lmweb[place_id] = lmfromtext(text_web)

        cur.execute('select text from sample where place_id = \'{0}\' order by rand()'.format(place_id))
        text_twt = [row['text'] for row in cur]
        lmtwt[place_id] = lmfromtext(text_twt)

    # calculate the KLD for each pair of tweets and web pages
    # and rank the lmweb
    score = Dataset()
    for pid_twt in lmtwt.iterkeys():
        rank = list()
        for pid_web in lmweb.iterkeys():
            rank.append((place_name(pid_web),
                kl_divergence(lmweb[pid_web], lmtwt[pid_twt])))
        score[place_name(pid_twt)] = [pname for pname, kld in \
                sorted(rank, key=itemgetter(1), reverse=False)]

    #score.write2csv('rank.lst', False)
    return score


def evaluate(ranks):
    prec = list()
    for pos in range(0, ranks.size()):
        goal = 0
        for query in ranks.iterkeys():
            if query in set(ranks[query][:pos]):
                goal += 1
        prec.append(goal / float(len(ranks)))
    plt.plot(range(0, ranks.size()), prec)
    plt.xlabel('List Length')
    plt.ylabel('Goal Rate')
    plt.title('Goal Graph')
    plt.show()

def expr():
    evaluate(web_based_guess())

if __name__ == '__main__':
    expr()

