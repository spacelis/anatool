import pdb
#!python
# -*- coding: utf-8 -*-
"""File: visual.py
Description:
    This module contains visualizing method for geo data
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import dataset
from anatool.dm.db import GEOTWEET
import text_util
from operator import itemgetter
import time
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pymaps

import seaborn as sns
sns.set_palette("deep", desat=.6)
sns.set_style("white")
sns.set_context(font_scale=1.5, rc={"figure.figsize": (3, 2), 'axes.grid': False, 'axes.linewidth': 1,})


def cnt_poi(city, table='sample'):
    """ Draw the tweet distribution over POIs."""
    twt_lst = dataset.loadrows(GEOTWEET, ('place_id', 'count(id) as cnt'),
                               "superior_id='%s'" % (city), table, 'group by place_id')


def cnt_map(region, table = 'sample', draw = True):
    """Draw a region map of tweets"""
    twt_lst = dataset.loadrows(GEOTWEET, ('lat', 'lng'),
            ('MBRContains({0}, geo)'.format(dataset.geo_rect(*region)),), table)
    lat = list();
    lng = list();
    for twt in twt_lst:
        lat.append(twt['lat'])
        lng.append(twt['lng'])
    if draw:
        x = np.array(lng)
        y = np.array(lat)
        xmin = x.min()
        xmax = x.max()
        ymin = y.min()
        ymax = y.max()

        plt.hexbin(x,y, gridsize=200, cmap=cm.jet)
        plt.axis([xmin, xmax, ymin, ymax])
        plt.title("Hexagon binning")
        cb = plt.colorbar()
        cb.set_label('counts')

        plt.show()
    return lat, lng


def word_freq(twt_lst, unit = '', table = 'sample', draw = True):
    """show the word count in the twt_lst"""
    dist = dict()
    for twt in twt_lst:
        token_dist = text_util.line2tf(text_util.fourq_filter(twt['text']))
        if unit == '':
            text_util.accum_dist(dist, token_dist)
        elif unit == 'tweet':
            for t in token_dist.iterkeys():
                if t in dist:
                    dist[t] += 1
                else:
                    dist[t] = 1
        elif unit == 'poi':
            for t in token_dist.iterkeys():
                if t in dist:
                    dist[t].add(twt['place_id'])
                else:
                    dist[t] = set((twt['place_id'],))

    dist2 = dict()
    for key in dist.iterkeys():
        if unit == '' or unit == 'tweet':
            if dist[key] > 1:
                dist2[key] = dist[key]
        elif unit == 'poi':
            if len(dist[key]) > 1:
                dist2[key] = len(dist[key])

    del dist
    sortdist = sorted(dist2.iteritems(), key=itemgetter(1), reverse=True)

    if draw:
        width = 0.35
        idx = np.arange(len(sortdist))
        plt.bar(idx, [val for key, val in sortdist])
        plt.ylabel('Freq')
        plt.title('Sorted Words Frequency')
        #plt.xticks(idx+width/2., [key for key, val in sortdist] )

        plt.show()
    return sortdist

def poi_freq(twt_lst, table = 'sample', draw = True):
    """Draw a bar chart of the distribution of tweets among pois"""
    dist = dict()

def geo_map(dst, data_lst):
    """Generate a HTML file to use Google maps to display"""
    gmap = pymaps.PyMap()
    gmap.maps[0].zoom = 5
    for item in data_lst:
        gmap.maps[0].setpoint([item['lat'], item['lng'], \
                '{0},{1}<br>{2}'.format(item['lat'], item['lng'], item['text'])])
    open(dst,'wb').write(gmap.showhtml())   # generate test file

def top_poi100_map():
    plc_lst = dataset.loadrows(GEOTWEET, ('lat', 'lng', 'name'), ('superior_name=\'los angeles\'',), 'sample_dist_100')
    for plc in plc_lst:
        plc['text'] = plc['name']
    geo_map('../la_100.html', plc_lst)

def region_dist(dst, region):
    """draw a map of region"""
    plc_lst = dataset.qloadrows(GEOTWEET, 'SELECT place_id, place.name, count(place_id) as cnt, place.lat, place.lng from sample left join place on sample.place_id = place.id where MBRContains({0}, place.geo) group by place_id'.format(text_util.geo_rect(*region)))
    for plc in plc_lst:
        plc['text'] = plc['name'] + ',' + str(plc['cnt'])
    geo_map(dst, plc_lst)



class id2int(object):
    """map ids to an int
    """
    def __init__(self):
        """docstring for __init__
        """
        self.idlist = dict()

    def map(self, idstr):
        """map idstr to an int
        """
        if idstr not in self.idlist:
            self.idlist[idstr] = len(self.idlist)
        return self.idlist[idstr]


def time_place_plot(user_id):
    """plot the time of each tweet in a day
    """
    tims = list()
    plcs = list()
    idm = id2int()
    rows = dataset.loadrows(GEOTWEET, ('created_at', 'place_id'), ('user_id={0}'.format(user_id),), 'sample')
    for line in rows:
        if line['created_at'] == None:
            continue
        tim = time.strptime(str(line['created_at']), '%Y-%m-%d %H:%M:%S')
        plc = line['place_id']
        tims.append(tim.tm_wday + tim.tm_hour/24.0)
        plcs.append(idm.map(plc))
    x = np.array(tims)
    y = np.array(plcs)
    plt.plot(x, y, 'o')
    plt.title('User {0}'.format(user_id))
    plt.show()


def time_plot(place_id):
    """plot the time of each tweet in a day
    """
    tims = list()
    plcs = list()
    idm = id2int()
    rows = dataset.loadrows(GEOTWEET, ('created_at',), ('place_id=\'{0}\''.format(place_id),), 'sample')
    for line in rows:
        if line['created_at'] == None:
            continue
        tim = time.strptime(str(line['created_at']), '%Y-%m-%d %H:%M:%S')
        tims.append(tim.tm_wday + tim.tm_hour/24.0)
    x = np.array(tims)
    plt.hist(x, 42)
    plt.title('Place {0}'.format(place_id))
    plt.show()



if __name__ == '__main__':
    #show_cnt_map(((40.67,-74.05),(40.75,-73.93)), 'tweet')
    #from analyze import sampling
    #dist = word_freq(sampling.sample_by_region(((40.75,-74.02),(40.70,-73.97))), 'poi')
    #for i in range(100):
        #print dist[i]
    #top_poi100_map()
    #region_dist('manhatton.html', ((40.75, -74.00), (40.745, -73.995)))
    #time_plot('../data/list/38062252_time.csv')
    # time_plot('ee858ad43eb4072e')
    cnt_poi()
