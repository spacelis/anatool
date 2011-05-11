"""File: dataset.py
Description:
This module contains all the data model used in analysis
History:
    0.2.3: + csv output for Dataset
    0.2.2: + Dataset, DataItem classes
    0.2.1: add lots of things
    0.1.1: Add class DataColumnIterator
    0.1.0: The first version
"""

__version__ = '0.2.3'
__author__ = 'SpaceLis'

import random, csv
from anatool.dm.db import CONN_POOL, GEOTWEET
from anatool.analyze.text_util import geo_rect
from annotation import Cache

#---------------------------------------------------------- List Operators
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
    length = len(lst) / cnt
    pos = 0
    for idx in range(cnt - 1):
        pivot.append(lst[pos:pos+length])
        pos += length
    pivot.append(lst[pos:])
    return pivot

#---------------------------------------------------------- Dataset
class Dataset(dict):
    """Dataset is a column oriented data storage. The key is the title of the
    column while the value is the list of data in the column (key) in a
    sequential order.
    """
    def __init__(self, *arg, **karg):
        super(Dataset, self).__init__(*arg, **karg)
        self.sortedkey = None

    def size(self):
        """the size of the dataset, i.e., the number of rows
        """
        if len(self) == 0:
            return 0
        return len(self.itervalues().next())

    def append(self, item):
        """Add a new data item into the dataset
        This is just for mocking list().append()
        """
        for key in item.iterkeys():
            if key not in self:
                # TODO add default values for unseen key
                self[key] = [0 for idx in range(self.size())]
            self[key].append(item[key])

    def extend(self, itemlist):
        """Extend the dataset with the itemlist
        This is just for mocking list().extend()
        """
        for item in itemlist:
            self.append(item)

    def distinct(self, key):
        """Return the value set of the key
        """
        vset = set()
        for val in self[key]:
            vset.add(val)
        return [val for val in vset]

    def groupfunc(self, key, pkey, func):
        """Return the output of a function to the values grouped by key
        """
        rst = DataItem()
        if self.sortedkey == key:
            indices = range(self.size())
        else:
            indices = sorted(indices, key=lambda x:self[key][x])
        temp = list()
        idx_val = type(self[key][0]).__init__()
        for idx in indices:
            if idx_val != self[key][idx]:
                if len(temp)>0:
                    rst[idx_val] = func(temp)
                temp = list()
                idx_val = self[key][idx]
            temp.append(self[pkey][idx])
        rst[idx_val] = func(temp)
        return rst

    def merge(self, dset):
        """Merge the keys and values into this Dataset
        """
        if self.size() != dset.size():
            raise TypeError, "size doesn't match"
        for key in dset.iterkeys():
            if key not in self:
                self[key] = dset[key]
            else:
                raise TypeError, "Key conflicting"

    def item(self, idx):
        """Return the item at the position idx
        """
        rst = DataItem()
        for key in self.iterkeys():
            rst[key] = self[key][idx]
        return rst

    def write2csv(self, filename, transposed = False):
        """ write this dataset into a csv file
        """
        with open(filename, 'wb') as fout:
            csvwriter = csv.writer(fout, delimiter=';', quotechar='`')
            if not transposed:
                csvwriter.writerow([key for key in self.iterkeys()])
                for item in self:
                    csvwriter.writerow([item[key] for key in item.iterkeys()])
            else:
                for key in self.iterkeys():
                    csvwriter.writerow([key, ] + self[key])


    def __iter__(self):
        """Iterating items in the dataset
        """
        for idx in range(self.size()):
            yield self.item(idx)

class PartialIterator(object):
    """Iterator by an index list"""
    def __init__(self, dset, idc):
        super(PartialIterator, self).__init__()
        self._dset, self._idc = dset, idc
        self._idx = 0

    def __iter__(self):
        """Make it iterative"""
        for idx in self._idc:
            yield self._dset.item(idx)

class DataItem(dict):
    """Keeps data"""
    def __init__(self, *arg, **karg):
        super(DataItem, self).__init__(*arg, **karg)

    def accum_dist(self, src):
        """merge two distribution of words"""
        for key in src.iterkeys():
            if key in self.iterkeys():
                self[key] += src[key]
            else:
                self[key] = src[key]

#---------------------------------------------------------- Database Access
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
        twt = DataItem()
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
    return Dataset().extend([row for row in cur])

@Cache()
def place_name(pid, dbconf=GEOTWEET):
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

if __name__ == '__main__':
    #region2arff('test.arff', ((40.75,-74.02),(40.70,-73.97)))
    #d = Dataset([{'id':'a', 'val':1},
    #{'id':'b', 'val':1}, {'id':'a', 'val':2}])
    #print d
    #print d.groupfunc('id', len)
    #print list_split([1,2,3,4,5,6,7,8,9], 4)
    print place_name('0007a1bd373a2805')

