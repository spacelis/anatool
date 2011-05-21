#!python
# -*- coding: utf-8 -*-
"""File: result.py
Description:
    Analysis tools for WEKA prediction results
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import json
from operator import itemgetter
from anatool.analyze import weka
from anatool.analyze.text_util import fourq_filter, csv_filter
import dataset

def confusion_matrix(log, plcf, col):
    """generate type confusion matrix"""
    ins_lst = weka.log_parse(log)
    classes = set()
    places = dataset.DataItem()
    with open(plcf) as fplc:
        for line in fplc:
            place = json.loads(line)
            places[place[col]] = place
            classes.add(place[col])

    print classes

    cmat = dict()
    for ref in classes:
        cmat[ref] = dict()
        for prd in classes:
            cmat[ref][prd] = list()

    for ins in ins_lst:
        ref = places[ins['refN']][col]
        hyp = places[ins['prdN']][col]
        cmat[ref][hyp].append(int(ins['id']))

    return cmat

def count_matrix(mat):
    """return the count of each list in matrix"""
    rmat = dict()
    for i in mat:
        rmat[i] = dict()
        print '%3d' % int(i),
        for j in mat:
            rmat[i][j] = len(mat[i][j])
            print '%4d' % rmat[i][j],
        print
    return rmat

def err_analyze(dst, mat, twtf, plcf, col):
    """output csv for mat"""
    twt_lst = dataset.Dataset()
    with open(twtf) as ftwt:
        for line in ftwt:
            twt_lst.append(json.loads(line))

    places = dataset.DataItem()
    with open(plcf) as fplc:
        for line in fplc:
            place = json.loads(line)
            places[place[col]] = place

    with open(dst, 'w') as fdst:
        print >>fdst, '"Ref POI", "Hyp POI", "Text", "Ref Genre", "Hyp Genre", "Ref SGenre", "Hyp SGenre"'
        for i in mat:
            for j in mat:
                #if i != j:
                    for item in mat[i][j]:
                        #              ref    hyp  text  rcat  hcat   rsc   hsc
                        try:
                            print >>fdst, '"{0}","{1}","{2}","{3}","{4}","{5}","{6}"' \
                                .format(csv_filter(places[i]['name']),csv_filter(places[j]['name']), \
                                fourq_filter(csv_filter(twt_lst[item]['text'])), \
                                places[i]['category'],places[j]['category'], \
                                places[i]['super_category'], places[j]['super_category'])
                        except: pass

def catelist(src, col):
    """generate list of col for picturing confusion matrix"""
    places = dict()
    with open(src) as fsrc:
        for line in fsrc:
            place = json.loads(line)
            places[place[col]] = place['label']
    print "'" + "','".join(sorted(places, key=places.__getitem__)) + "'"

def thirgest(log):
    """The accuracy in first three"""
    threshold = 3
    ins_lst = weka.log_parse(log)
    pos, cnt = 0, 0
    for ins in ins_lst:
        #print ins['score']
        rnk = sorted(zip(ins['score'], range(1, len(ins['score']) + 1)), \
                key=lambda x: x[0], reverse=True)
        #print rnk
        for i in range(threshold):
            if rnk[i][1] == ins['ref']:
                pos += 1
                break
        #print pos
        #if cnt>10: return
        cnt += 1
    return pos/float(cnt)

if __name__ == '__main__':
    #cmat = confusion_matrix('../weka2/chicago_no_fold.log', '../weka2/chicago.arff.place', 'label')
    #err_analyze('../weka2/chicago.errxs.csv', cmat, '../weka2/chicago.arff.tweet', '../weka2/chicago.arff.place', 'label')
    #cmat = confusion_matrix('../weka2/la_no_fold.log', '../weka2/la.arff.place', 'label')
    #err_analyze('../weka2/la.errxs.csv', cmat, '../weka2/la.arff.tweet', '../weka2/la.arff.place', 'label')
    #cmat = confusion_matrix('../weka2/new_york_no_fold.log', '../weka2/new_york.arff.place', 'label')
    #err_analyze('../weka2/new_york.errxs.csv', cmat, '../weka2/new_york.arff.tweet', '../weka2/new_york.arff.place', 'label')
    #cmat = confusion_matrix('../weka2/san_fran_no_fold.log', '../weka2/san_fran.arff.place', 'label')
    #err_analyze('../weka2/san_fran.errxs.csv', cmat, '../weka2/san_fran.arff.tweet', '../weka2/san_fran.arff.place', 'label')
    #catelist('../weka2/chicago_type.arff.place', 'category')
    #catelist('../weka2/new_york_type.arff.place', 'category')
    #catelist('../weka2/la_type.arff.place', 'category')
    #catelist('../weka2/san_fran_type.arff.place', 'category')
