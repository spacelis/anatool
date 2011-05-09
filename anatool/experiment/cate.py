#!python
# -*- coding: utf-8 -*-
"""File: baseline.py
Description:
    Contains baseline experiments
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import dataset
import math
from operator import itemgetter
import json
from anatool.dm.db import GEOTWEET
from anatool.analyze.text_util import line2tf, comma_filter, name_filter, fourq_filter, geo_rect
import smoothing

def top_poi_100(dst, city, col):
    """Select all POIs from New York as the candidates"""
    plst = dataset.loadrows(GEOTWEET, ('id',), \
            ('superior_name=\'{0}\''.format(city),), 'sample_dist_100')
    twt_lst = dataset.load_by_place([plc['id'] for plc in plst])

    places = dataset.DataItem()
    vec_lst = dataset.Dataset()
    for twt in twt_lst:
        vec_lst.append(line2tf(comma_filter(fourq_filter(twt['text']))))
        if twt['place_id'] not in places:
            place = dataset.DataItem()
            place['id'] = twt['place_id']
            place['label'] = str(len(places))
            place['name'] = twt['name']
            place['category'] = twt['category']
            place['super_category'] = twt['super_category']
            places[twt['place_id']] = place

    #output the places as json objects
    with open(dst + '.place', 'w') as fplc:
        for key in places:
            print >>fplc, json.dumps(places[key])

    #output the tweets as json objects
    with open(dst + '.tweet', 'w') as ftwt:
        i = 0
        for twt in twt_lst:
            print >>ftwt, json.dumps(twt)

    #cut all the key that only appear less than 3 times
    bgdist = vec_lst.bgdist()


    keylist = list()
    keylist.append('__NO__')
    keylist.extend([key for key in bgdist.iterkeys() if bgdist[key]>3])
    keylist.append('__CLASS__')

    # add idf divisor
    #idf = vec_lst.idf()
    #for vec in vec_lst:
        #for key in vec.iterkeys():
            #vec[key] = vec[key]/math.log(float(idf[key])+1)



    for i in range(len(vec_lst)):
        vec_lst[i]['__CLASS__'] = name_filter(places[twt_lst[i]['place_id']][col])
        vec_lst[i]['__NO__'] = i

    #def wdist(vec_lst):
        #"""get the back ground distribution"""
        #bgdist = dict()
        #for vec in vec_lst:
            #for key in vec.iterkeys():
                #if key in bgdist:
                    #bgdist[key] += vec[key]
                #else:
                    #bgdist[key] = vec[key]
        #return bgdist
    #wpdist = vec_lst.groupfunc('__CLASS__', wdist)
    #for key in wpdist.iterkeys():
        #print (sorted(wpdist[key], key=itemgetter(1), reverse=True))[0:10]
    vec_lst.gen_arff(dst, keylist)

def all_poi_100(dst, col):
    """Select all POIs from New York as the candidates"""
    plst = dataset.loadrows(GEOTWEET, ('id',), \
            None, 'sample_dist_100')
    twt_lst = dataset.load_by_place([plc['id'] for plc in plst])

    places = dataset.DataItem()
    vec_lst = dataset.Dataset()
    for twt in twt_lst:
        vec_lst.append(line2tf(comma_filter(fourq_filter(twt['text']))))
        if twt['place_id'] not in places:
            place = dataset.DataItem()
            place['id'] = twt['place_id']
            place['label'] = str(len(places))
            place['name'] = twt['name']
            place['category'] = twt['category']
            place['super_category'] = twt['super_category']
            places[twt['place_id']] = place

    #output the places as json objects
    with open(dst + '.place', 'w') as fplc:
        for key in places:
            print >>fplc, json.dumps(places[key])

    #output the tweets as json objects
    with open(dst + '.tweet', 'w') as ftwt:
        i = 0
        for twt in twt_lst:
            print >>ftwt, json.dumps(twt)

    #cut all the key that only appear less than 3 times
    bgdist = vec_lst.bgdist()


    keylist = list()
    keylist.append('__NO__')
    keylist.extend([key for key in bgdist.iterkeys() if bgdist[key]>3])
    keylist.append('__CLASS__')

    # add idf divisor
    #idf = vec_lst.idf()
    #for vec in vec_lst:
        #for key in vec.iterkeys():
            #vec[key] = vec[key]/math.log(float(idf[key])+1)



    for i in range(len(vec_lst)):
        vec_lst[i]['__CLASS__'] = name_filter(places[twt_lst[i]['place_id']][col])
        vec_lst[i]['__NO__'] = i

    #def wdist(vec_lst):
        #"""get the back ground distribution"""
        #bgdist = dict()
        #for vec in vec_lst:
            #for key in vec.iterkeys():
                #if key in bgdist:
                    #bgdist[key] += vec[key]
                #else:
                    #bgdist[key] = vec[key]
        #return bgdist
    #wpdist = vec_lst.groupfunc('__CLASS__', wdist)
    #for key in wpdist.iterkeys():
        #print (sorted(wpdist[key], key=itemgetter(1), reverse=True))[0:10]
    vec_lst.gen_arff(dst, keylist)

def top_poi_100_crs(dst, city, col):
    """Select all POIs from New York as the candidates"""
    plst = dataset.loadrows(GEOTWEET, ('id',), \
            ('superior_name=\'{0}\''.format(city),), 'sample_dist_100')
    twt_lst = dataset.load_by_place([plc['id'] for plc in plst])

    places = dataset.DataItem()
    vec_lst = dataset.Dataset()
    for twt in twt_lst:
        vec_lst.append(line2tf(comma_filter(fourq_filter(twt['text']))))
        if twt['place_id'] not in places:
            place = dataset.DataItem()
            place['id'] = twt['place_id']
            place['label'] = str(len(places))
            place['name'] = twt['name']
            place['category'] = twt['category']
            place['super_category'] = twt['super_category']
            places[twt['place_id']] = place

    #output the places as json objects
    with open(dst + '.place', 'w') as fplc:
        for key in places:
            print >>fplc, json.dumps(places[key])

    #output the tweets as json objects
    with open(dst + '.tweet', 'w') as ftwt:
        i = 0
        for twt in twt_lst:
            print >>ftwt, json.dumps(twt)

    #cut all the key that only appear less than 3 times
    bgdist = vec_lst.bgdist()

    keylist = list()
    keylist.append('__NO__')
    keylist.extend([key for key in bgdist.iterkeys() if bgdist[key]>3])

    keylist.append('__CLASS__')
    for i in range(len(vec_lst)):
        vec_lst[i]['__CLASS__'] = places[twt_lst[i]['place_id']][col]
        vec_lst[i]['__NO__'] = i
    vec_lst.gen_crs_arff(dst,5 , keylist)

def region2arff(dst, region):
    """Generate data in the region in arff format"""
    twt_lst = dataset.loadrows(GEOTWEET, ('place_id', 'text'),
            ('MBRContains({0}, geo)'.format(geo_rect(*region)),))
    vec_lst = dataset.Dataset([line2tf(comma_filter(fourq_filter(twt['text']))) \
            for twt in twt_lst])
    bgdist = vec_lst.bgdist()
    #cut all the key that only appear less than 3 times
    keylist = [key for key in bgdist.iterkeys() if bgdist[key]>3]

    keylist.append('__CLASS__')
    for i in range(len(vec_lst)):
        vec_lst[i]['__CLASS__'] = twt_lst[i]['place_id']
    vec_lst.gen_arff(dst, keylist)

def cate_smoothed_100(dst, city):
    """Select all POIs from New York as the candidates"""
    plst = dataset.loadrows(GEOTWEET, ('id',), \
            ('superior_name=\'{0}\''.format(city),), 'sample_dist_100')
    twt_lst = dataset.load_by_place([plc['id'] for plc in plst])

    twt_lst = smoothing.cate_smooth(twt_lst, 1, lambda x,y: True)

    vec_lst = dataset.Dataset([line2tf(comma_filter(fourq_filter(twt['text']))) for twt in twt_lst])

    bgdist = vec_lst.bgdist()

    #cut all the key that only appear less than 3 times
    keylist = [key for key in bgdist.iterkeys() if bgdist[key]>3]

    keylist.append('__CLASS__')

    for i in range(len(vec_lst)):
        vec_lst[i]['__CLASS__'] = name_filter(dataset.place_name(twt_lst[i]['place_id'], GEOTWEET))
    statistics.class_dist(vec)
    vec_lst.gen_arff(dst, keylist)



if __name__ == '__main__':
    #top_poi_100('../weka2/new_york.arff', 'New York', 'label')
    #top_poi_100('../weka2/san_fran.arff', 'San Francisco', 'label')
    #top_poi_100('../weka2/Chicago.arff', 'Chicago', 'label')
    #top_poi_100('../weka2/LA.arff', 'Los Angeles', 'label')
    #all_poi_100('../weka2/all.arff', 'label')
    #top_poi_100_crs('../weka3/new_york', 'New York', 'label')
    #top_poi_100_crs('../weka3/san_fran', 'San Francisco', 'label')
    #top_poi_100_crs('../weka3/Chicago', 'Chicago', 'label')
    #top_poi_100_crs('../weka3/LA', 'Los Angeles', 'label')
    #top_poi_100_all('../weka/all.arff')
    #region2arff('../weka/mahatton.arff', ((40.75, -74.00), (40.745, -73.995)))
    #cate_smoothed_100('../weka/new_york100s.arff', 'New York')
    #cate_smoothed_100('../weka/san_fran100s.arff', 'San Francisco')
    #cate_smoothed_100('../weka/Chicago100s.arff', 'Chicago')
    #cate_smoothed_100('../weka/LA100s.arff', 'Los Angeles')
    #print thirgest('../weka/sf_smo.log')
    pass



