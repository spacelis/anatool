#!python
# -*- coding: utf-8 -*-
"""File: weka.py
Description: Link WEKA into the project
History:
    0.2.0 + a group of functions to interact with WEKA
    0.1.0 The first version.
"""
__version__ = '0.2.0'
__author__ = 'SpaceLis'

import re, random
from anatool.dm.db import CONN_POOL, GEOTWEET
from anatool.analyze.dataset import loadrows, Dataset, DataItem, list_split
from anatool.analyze.text_util import geo_rect

_SPACE = re.compile(r'\s+')
_SYMBOL = re.compile(r'\+|\*')
_CLSNO = re.compile(r':')
_PARATH = re.compile(r'\(|\)')

def gen_arff(dset, dst, key_lst=None, \
        typemap=dict({'__CLASS__': 'DISC'}), \
        default_type = 'NUMERIC'):
    """Generate arff file for WEKA"""
    farff = open(dst, 'w')
    print >> farff, '@Relation {0}'.format(dst)

    #Build the universe term set
    if key_lst == None:
        key_set = set()
        for twt in dset:
            for key in twt.iterkeys():
                key_set.add(key)
        key_lst = sorted(key_set)

    #Build the universe class set
    dis_lst = dict()
    for key in key_lst:
        if typemap.get(key, default_type) == 'DISC':
            dis_lst[key] = set()
    for item in dset:
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
    for item in dset:
        print >> farff, ', '.join(str(item.get(key, 0)) for key in key_lst)

    farff.flush()
    farff.close()


def gen_crs_arff(self, dst, fold, key_lst=None, \
        typemap=dict({'__CLASS__': 'DISC'}), \
        default_type = 'NUMERIC'):
    """generate dataset for cross validation"""
    clses = dict()
    for i in range(len(self)):
        if self[i]['__CLASS__'] not in clses:
            clses[self[i]['__CLASS__']] = dict()
            clses[self[i]['__CLASS__']]['list'] = list()
        clses[self[i]['__CLASS__']]['list'].append(i)
    for cls in clses:
        random.shuffle(clses[cls]['list'])
        clses[cls]['fold'] = list_split(clses[cls]['list'], fold)
    for i in range(fold):
        test = Dataset()
        train = Dataset()
        for cls in clses.iterkeys():
            test.extend([self[f] for f in clses[cls]['fold'][i]])
            for j in range(fold):
                if j != i:
                    train.extend([self[f] for f in clses[cls]['fold'][j]])
        gen_arff(test, '{0}.test.{1}.arff'.format(dst, i), key_lst, \
                typemap, default_type)
        gen_arff(train, '{0}.train.{1}.arff'.format(dst, i), key_lst, \
                typemap, default_type)

def log_parse(src):
    """parse predication output from WEKA"""
    ins_lst = Dataset()
    with open(src) as fsrc:
        for line in fsrc:
            line, dummy = _SYMBOL.subn(' ', line)
            col = _SPACE.split(line)
            ins = DataItem()
            ins['ref'] = int((_CLSNO.split(col[2]))[0])
            ins['refN'] = (_CLSNO.split(col[2]))[1]
            ins['prd'] = int((_CLSNO.split(col[3]))[0])
            ins['prdN'] = (_CLSNO.split(col[3]))[1]
            ins['err'] = True if col[4] == '+' else False
            ins['score'] = [float(col[i]) for i in range(4, len(col) - 2)]
            ids, dummy = _PARATH.subn('', col[len(col) - 2])
            ins['id'] = int(ids)
            ins_lst.append(ins)
    return ins_lst

def run_weka(cmdline):
    """Run WEKA classifiers and return the output log in string format
    """
    #FIXME implement the code for it
    pass

def test():
    """Test this unit"""
    twt_lst = loadrows(GEOTWEET, ('place_id', 'text'),
            ('MBRContains({0}, geo)'.format(\
                    geo_rect((40.75,-74.02),(40.70,-73.97))),))
    gen_arff(twt_lst, 'test.arff', {'text': 'TEXT', 'place_id': 'DISC'})


if __name__ == '__main__':
    log_parse('../weka/chicago_type.log')
