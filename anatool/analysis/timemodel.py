#!python
# -*- coding: utf-8 -*-
"""File: time_analysis.py
Description:
    Analyze the time series of tweets
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

from anatool.dm.dataset import DataItem
from anatool.analysis.feature import norm_v1
from datetime import datetime

class TimeModel(object):
    """ Time Model will capture the return period of ticks
    """

    def __init__(self, ticks):
        super(TimeModel, self).__init__()
        self.hourdist = DataItem([(i, 0) for i in range(6)])
        self.wdaydist = DataItem([(i, 0) for i in range(7)])
        self.mdaydist = DataItem([(i, 0) for i in range(32)])
        if isinstance(ticks[0], datetime):
            for i in range(len(ticks)):
                ticks[i] = ticks[i].timetuple()
        for tick in ticks:
            self.hourdist[tick.tm_hour / 4] += 1
            self.mdaydist[tick.tm_mday] += 1
            self.wdaydist[tick.tm_wday] += 1
        self.hourdist = norm_v1(self.hourdist)
        self.wdaydist = norm_v1(self.wdaydist)
        self.mdaydist = norm_v1(self.mdaydist)

    def score(self, tm, **kargs):
        """ score is based on the distribution of the tick in period dimension
        """
        hs, ws, ms = 0.0, 0.0, 0.0
        for i in range(6):
            hs += self.hourdist[i] * tm.hourdist[i]
            ws += self.wdaydist[i] * tm.wdaydist[i]
        for i in range(32):
            ms += self.mdaydist[i] * tm.mdaydist[i]

        if 'balance' not in kargs:
            return 0.4*hs + 0.4*ws + 0.2*ms

        return kargs['balance'][0] * hs \
                + kargs['balance'][1] * ws \
                + kargs['balance'][2] * ms

    def isasc(self):
        """ Return 0 indicating the larger the more similar
        """
        return False

def test():
    """ test this module
    """



if __name__ == '__main__':
    test()
