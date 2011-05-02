"""File: dataset.py
Description:
This module contains all the data model used in analysis
History:
    0.2.2: + Dataset, DataItem classes
    0.2.1: add lots of things
    0.1.1: Add class DataColumnIterator
    0.1.0: The first version
"""

__version__ = '0.2.2'
__author__ = 'SpaceLis'

import random
from anatool.dm.db import CONN_POOL, GEOTWEET
from anatool.analyze.text_util import line2tf, comma_filter, fourq_filter, geo_rect

def rand_select(cnt, ratio):
    """Generate two list of random numbers below cnt, the length of
    the two lists are at the ratio"""
    lst = range(0, cnt)
    random.shuffle(lst)
    pivot = int(cnt * ratio)
    return lst[:pivot - 1], lst[pivot:]

def ratio_select(cnt, ratio):
    """Generate two list of consecutive numbers according to the ratio"""
    return range(0, int(cnt * ratio)), range(int(cnt * ratio), cnt)

def list_split(lst, cnt):
    """splite list into cnt parts"""
    pivot = list()
    l = len(lst) / cnt
    p = 0
    for i in range(cnt - 1):
        pivot.append(lst[p:p+l])
        p += l
    pivot.append(lst[p:])
    return pivot


class Dataset(list):
    """Keep a list of dict object"""
    def __init__(self, *arg, **karg):
        super(Dataset, self).__init__(*arg, **karg)

    def gen_arff(self, dst, key_lst=None, \
            typemap=dict({'__CLASS__': 'DISC'}), \
            default_type = 'NUMERIC'):
        """Generate arff file for WEKA"""
        farff = open(dst, 'w')
        print >> farff, '@Relation {0}'.format(dst)

        #Build the universe term set
        if key_lst == None:
            key_set = set()
            for twt in self:
                for key in twt.iterkeys():
                    key_set.add(key)
            key_lst = sorted(key_set)

        #Build the universe class set
        dis_lst = dict()
        for key in key_lst:
            if typemap.get(key, default_type) == 'DISC':
                dis_lst[key] = set()
        for item in self:
            for key in dis_lst.iterkeys():
                if item[key] not in dis_lst[key]:
                    dis_lst[key].add(item[key])

        #Generate column description
        for key in key_lst:
            if typemap.get(key, default_type) == 'DISC':
                print >> farff, '@ATTRIBUTE {0}\t{{'.format(key),
                print >> farff, ', '.join(val for val in dis_lst[key]),
                print >> farff, '}'
            else:
                print >> farff, '@ATTRIBUTE {0}\t{1}'.\
                        format(key, typemap.get(key, default_type))

        #Generate dataset
        print >> farff, '@DATA'
        for item in self:
            print >> farff, ', '.join(str(item.get(key, 0)) for key in key_lst)

        farff.flush()
        farff.close()

    def gen_crs_arff(self, dst, fold, key_lst=None, \
            typemap=dict({'__CLASS__': 'DISC'}), \
            default_type = 'NUMERIC'):
        """generate dataset for cross validation"""
        cls = dict()
        for i in range(len(self)):
            if self[i]['__CLASS__'] not in cls:
                cls[self[i]['__CLASS__']] = dict()
                cls[self[i]['__CLASS__']]['list'] = list()
            cls[self[i]['__CLASS__']]['list'].append(i)
        for c in cls.iterkeys():
            random.shuffle(cls[c]['list'])
            cls[c]['fold'] = list_split(cls[c]['list'], fold)
        for i in range(fold):
            test = Dataset()
            train = Dataset()
            for c in cls.iterkeys():
                test.extend([self[f] for f in cls[c]['fold'][i]])
                for j in range(fold):
                    if j != i:
                        train.extend([self[f] for f in cls[c]['fold'][j]])
            test.gen_arff('{0}.test.{1}.arff'.format(dst, i), key_lst, \
                    typemap, default_type)
            train.gen_arff('{0}.train.{1}.arff'.format(dst, i), key_lst, \
                    typemap, default_type)


    def bgdist(self):
        """get the back ground distribution"""
        bgdist = DataItem()
        for vec in self:
            for key in vec.iterkeys():
                if key in bgdist:
                    bgdist[key] += vec[key]
                else:
                    bgdist[key] = vec[key]
        return bgdist

    def distinct(self, column):
        """Return the value set of the column"""
        vset = set()
        for vec in self:
            vset.add(vec[column])
        return [val for val in vset]

    def groupfunc(self, column, func):
        """Return the output of a function to the values grouped by column"""
        rst = DataItem()
        self = sorted(self, key=lambda x:x[column])
        temp = list()
        col_val = ''
        for vec in self:
            if col_val != vec[column]:
                if len(temp)>0: rst[col_val] = func(temp)
                temp = list()
                col_val = vec[column]
            temp.append(vec)
        rst[col_val] = func(temp)
        return rst

    def idf(self):
        """get the idf distribution"""
        idfdist = dict()
        for vec in self:
            for key in vec.iterkeys():
                if key in idfdist:
                    idfdist[key] += 1
                else:
                    idfdist[key] = 1
        return idfdist


def loadrows(config, cols, wheres=None, table='sample', other=''):
    """Load tweets to list on conditions"""
    query = 'SELECT ' +  \
            ((', '.join(cols)) if cols!='*' else '*') \
            + ' FROM ' + table + \
            ((' WHERE ' + ' AND '.join(wheres)) if wheres else '') \
            + other
    cur = CONN_POOL.get_cur(config)
    print query
    cur.execute(query)
    res = Dataset()
    for row in cur:
        twt = dict()
        for key in cols:
            twt[key] = row[key]
        res.append(twt)
    print 'Count: {0}'.format(cur.rowcount)
    return res

def qloadrows(config, query):
    """Load tweets to list on conditions"""
    cur = CONN_POOL.get_cur(config)
    print query
    cur.execute(query)
    return Dataset([row for row in cur])

class PartialIterator(object):
    """Iterator by an index list"""
    def __init__(self, dset, idc):
        super(PartialIterator, self).__init__()
        self._dset, self._idc = dset, idc
        self._idx = 0

    def next(self):
        """Return the next element in the iterating list"""
        if self._idx >= len(self._idc):
            raise StopIteration
        else:
            self._idx += 1
            return self._dset[self._idc[self._idx - 1]]

    def prev(self):
        """Return the next element in the iterating list"""
        if self._idx < 0:
            raise StopIteration
        else:
            self._idx -= 1
            return self._dset[self._idc[self._idx + 1]]

    def __iter__(self):
        """Make it iterative"""
        return self


class DataItem(dict):
    """Keeps data"""
    def __init__(self, *arg, **karg):
        super(DataItem, self).__init__(*arg, **karg)


    def accum_dist(self, src):
        """merge two distribution of words"""
        for key in src.iterkeys():
            if key in self:
                self[key] += src[key]
            else:
                self[key] = src[key]

def place_name(pid, dbconf):
    """Return place name given a pid"""
    cur = CONN_POOL.get_cur(dbconf)
    cur.execute("select name from place where id=%s", pid)
    return cur.fetchone()['name']

def city_random(pid, cnt=10000):
    """Randomly select some tweets from the city"""
    return qloadrows(GEOTWEET, \
            'SELECT sample.id as id, text, sample.lat, sample.lng \
            from sample left join place on sample.place_id = place.id \
            where place.superior_id = \'{0}\' LIMIT {1}'.format(pid, cnt))

def type_random(typ, cnt=10000):
    """Randomly select some tweets from the place of the type"""
    return qloadrows(GEOTWEET, \
            'SELECT sample.id as id, place_id, text, sample.lat, sample.lng \
            from sample left join place on sample.place_id = place.id \
            where place.super_category = \'{0}\' LIMIT {1}'.format(typ, cnt))

def load_by_place(src):
    """Return samples according to the place list provided by src"""
    twt_lst = Dataset()
    for place in src:
        print place.strip()
        q_twt = qloadrows(GEOTWEET, \
                'SELECT sample.id, place_id, place.name, \
                    text, place.lat, place.lng, category, super_category \
                FROM sample left join place on sample.place_id = place.id \
                where place_id = \'{0}\''.format(place.strip()))
        twt_lst.extend(q_twt)
    print len(twt_lst)
    return twt_lst

def load_by_region(region):
    """Return samples according to the region"""
    return loadrows(GEOTWEET, \
            ('id', 'place_id', 'text', 'lat', 'lng'),
            ('MBRContains({0}, geo)'.format(geo_rect(*region)),))

def test():
    """Test this unit"""
    twt_lst = loadrows(GEOTWEET, ('place_id', 'text'),
            ('MBRContains({0}, geo)'.format(\
                    geo_rect((40.75,-74.02),(40.70,-73.97))),))
    twt_lst.gen_arff('test.arff', {'text': 'TEXT', 'place_id': 'DISC'})

if __name__ == '__main__':
    #region2arff('test.arff', ((40.75,-74.02),(40.70,-73.97)))
    #d = Dataset([{'id':'a', 'val':1}, {'id':'b', 'val':1}, {'id':'a', 'val':2}])
    #print d
    #print d.groupfunc('id', len)
    print list_split([1,2,3,4,5,6,7,8,9], 4)

