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

import re
import dataset

_SPACE = re.compile(r'\s+')
_SYMBOL = re.compile(r'\+|\*')
_CLSNO = re.compile(r':')
_PARATH = re.compile(r'\(|\)')

def log_parse(src):
    """parse predication output from WEKA"""
    ins_lst = dataset.Dataset()
    with open(src) as fsrc:
        for line in fsrc:
            line, dummy = _SYMBOL.subn(' ', line)
            col = _SPACE.split(line)
            ins = dataset.DataItem()
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



if __name__ == '__main__':
    log_parse('../weka/chicago_type.log')
