#!python
# -*- coding: utf-8 -*-
"""File: statistics.py
Description:
    This module contains some statistic functions.
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

from anatool.dm.db import CONN_POOL, GEOTWEET
import re
import dataset

def tweet_count(dbconf, table):
    """get count of tweets in database"""
    cur = CONN_POOL.get_cur(dbconf)
    cur.execute('select count(*) as cnt from {0}'.format(table))
    row = cur.fetchone()
    print 'Count:{0}'.format(row['cnt'])
    return row['cnt']

def foursq_count(dbconf, table):
    """get count that contains http://4sq.com"""
    foursq_pattern = re.compile(r'http://4sq.com')
    cur = CONN_POOL.get_cur(dbconf)
    cur.execute('select text from {0}'.format(table))
    k = 0
    for row in cur:
        if foursq_pattern.search(row['text']) != None:
            k += 1
    print 'Foursqure.com tweet count:{0}'.format(k)
    return k

def sub_place(pid, dbconf):
    """return a list of place contained within id"""
    cur = CONN_POOL.get_cur(dbconf)
    cur.execute("select id from place where superior_id=%s", pid)
    plc = set()
    for sub_pid in cur:
        plc.add(sub_pid['id'])
        plc.update(sub_place(sub_pid['id'], dbconf))
    return plc


def admin_dist(dbconf, pid):
    """get distribution of tweets in admin level"""
    cur = CONN_POOL.get_cur(dbconf)
    cur.execute("select id from place where superior_id=%s", pid)
    plcs = set()
    dist = dict()
    for row in cur:
        plcs = sub_place(row['id'], dbconf)
        dist[row['id']] = dict({'poi': len(plcs)})
        curx = CONN_POOL.get_cur(dbconf)
        for plc in plcs:
            curx.execute("select count(id) as cnt from sample where place_id=%s", plc)
            if 'cnt' not in dist[row['id']]:
                dist[row['id']]['cnt'] = curx.fetchone()['cnt']
            else:
                dist[row['id']]['cnt'] += curx.fetchone()['cnt']
    return dist


def class_dist(vec_lst):
    """display statistics of a dataset"""
    plc_dist = vec_lst.groupfunc('__CLASS__', len)
    for plc, cnt in plc_dist:
        print plc, cnt




if __name__ == '__main__':
    #tweet_count(GEOTWEET, 'sample')
    #foursq_count(GEOTWEET, 'sample')
    dist = admin_dist(GEOTWEET, '96683cc9126741d1')
    print '--dist--'
    for key in dist.iterkeys():
        print dataset.get_place_name(key, GEOTWEET),',', dist[key]['poi'], ',',dist[key]['cnt']


