#!python
# -*- coding: utf-8 -*-
"""File: websmooth.py
Description:
    Verifying whether the web pages from search engine can support tweets
    smoothing in place wise.
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import csv
from anatool.dm.db import CONN_POOL, GEOTWEET
from anatool.analyze.dataset import place_name
from anatool.analyze.lm import lmfromtext, kl_divergence

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

def expr():
    lm_comp()

if __name__ == '__main__':
    expr()



