#!python
# -*- coding: utf-8 -*-
"""File: smoothing.py
Description:
    Smoothing techniques are included here
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import dataset
from anatool.dm.db import GEOTWEET

def smoothing_by_city(twt_lst, city):
    """Smooth the tweet set"""
    pid_set = set()
    for twt in twt_lst:
        pid_set.add(twt['place_id'])

    for pid in pid_set:
        #FIXME
        pass


def rand_sel(twt, plc):
    """probably select a tweet"""
    #FIXME

def merge(dst_lst, twt_lst, pid):
    pidpool = set(dst_lst.distinct('place_id'))
    for twt in twt_lst:
        twt['place_id'] = pid
        if twt['id'] not in pidpool:
            dst_lst.append(twt)
    return dst_lst

def cate_smooth(twt_lst, ratio, sel, lmd):
    """Smoothing the dataset by place category"""
    rst_lst = dataset.Dataset()
    pid_lst = twt_lst.distinct('place_id')
    twt_dist = twt_lst.groupfunc('place_id', len)
    tid_set = set(twt_lst.distinct('place_id'))
    pid_set = set(pid_lst)

    for pid in pid_lst:
        plc = dataset.loadrows(GEOTWEET, ('id', 'lat', 'lng', 'super_category'), \
            ('id = \'{0}\''.format(pid),), 'place')
        plc_type = plc[0]['super_category']
        tmp_lst = list()
        cand = dataset.type_random(plc_type)

        for twt in cand:
            if twt['id'] not in tid_set and twt['place_id'] not in pid_lst:
                if sel(twt, plc):
                    twt['place_id'] = pid
                    tid_set.add(twt['id'])
                    pid_set.add(twt['place_id'])
                    tmp_lst.append(twt)
                if len(tmp_lst) >= ratio * twt_dist[pid]: break
        rst_lst.extend(tmp_lst)

    rst_lst.extend(twt_lst)

    return rst_lst

if __name__ == '__main__':
    twt_lst = cate_smooth(dataset.loadrows(GEOTWEET, ('text', 'place_id'), ('place_id = \'0002ac59702e20cf\'',)), 10, lambda x, y: True)
    print '----------------------'
    for twt in twt_lst:
        print twt

