#!python
# -*- coding: utf-8 -*-
"""File: text_util.py
Description: Contain some useful text manipulating functions
History:
    0.1.0 The first version.
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import re
from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer

_PATTERN_4SQ = [ re.compile(r'\sSt\.\s|\sRd\.\s'),
                re.compile(r'I\'m at.*?(?<!.\.\w|.\s\w)\.\s+'),
                re.compile(r'I\'m at.*?\s(?=http)'),
                re.compile(r'http://\S*'),
                re.compile(r'\(@.*\)')]
_COMMA = re.compile(r',')
_CSV = re.compile(r'"|,|\n|\r')
_SPACE = re.compile(r'\s+')
_NAMES = re.compile(r'\'|"|\(|\)|\s+|,')
_HTML = re.compile(r'<.*?>|&.*?;')

_ASIANCHAR = re.compile(u'[\u2E80-\u9FFF]')

_ANALYZER = StemmingAnalyzer()
# Alternative analyzer could be used
#from anatool.analyze.stopwords import STOPWORDS_RANKSNL_LONG
#_ANALYZER = StandardAnalyzer(stoplist = STOPWORDS_RANKSNL_LONG)


#------------------------------------------------------ Filters
def fourq_filter(line):
    """Filter out 4sq symbols"""
    for ptn in _PATTERN_4SQ:
        line, dummy = ptn.subn(r'', line)
    return line

def csv_filter(line):
    """ Filter out all comma and quote"""
    line, dummy = _CSV.subn(r'', line)
    return line

def comma_filter(line):
    """Remove all commas in a line"""
    line, dummy = _COMMA.subn(r' ', line)
    return line

def space_filter(line):
    """Remove all spaces in a line"""
    line, dummy = _SPACE.subn(r'_', line)
    return line

def name_filter(line):
    """Remove all commas in a line"""
    line, dummy = _NAMES.subn(r'_', line)
    return line

def html_filter(line):
    """Remove all HTML tags and escaped symbols
    """
    line, dummy = _HTML.subn(r'', line)
    return line

#------------------------------------------------------ Utils
def to_unicode(obj, encoding = 'utf-8'):
    """ convert line into unicode if possible
    """
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding, errors='ignore')
    return obj

def has_asianchar(line):
    """Return True if the line contains some Asian characters"""
    return _ASIANCHAR.search(line) != None

def geo_rect(pnt1, pnt2):
    """Generate geo string (Rectangle) for mysql"""
    _p1 = range(0, 2)
    _p2 = range(0, 2)
    _p1[0] = min(pnt1[0], pnt2[0])
    _p1[1] = min(pnt1[1], pnt2[1])
    _p2[0] = max(pnt1[0], pnt2[0])
    _p2[1] = max(pnt1[1], pnt2[1])

    return ' GeomFromText(\'Polygon(({0} {1}, {0} {3}, {2} {3}, {2} {1}, {0} {1}))\')'\
        .format(_p1[0], _p1[1], _p2[0], _p2[1])

#------------------------------------------------------ Tokenization
def get_tokens(line):
    """ return the token list of the line
    """
    line = fourq_filter(line)
    line = to_unicode(line)
    tokens = [token.text for token in _ANALYZER(line)]
    return tokens

def token_freq(token_lst):
    """Return the token distribution"""
    dist = dict()
    for t in token_lst:
        if not dist.has_key(t):
            dist[t] = 1
        else:
            dist[t] += 1
    return dist

def line2tf(line):
    """shortcut for token_freq(get_tokens())"""
    return token_freq(get_tokens(line))

def lines2tfidf(lines):
    """Construct a dataset of tfidf vectors from a set of string
    """
    #FIXME implement the code


if __name__ == '__main__':
    print fourq_filter('I\'m at Liberty Market (230 N. Gilbert Rd., Between Guadalupe & Elliot Roads @ Page Ave, Gilbert) w/ 2 others. http://4sq.com/3op0RO')
    print fourq_filter('I\'m at Max Karaoke LA Down Town (333 S Alameda St. #216 at E 3rd St Los Angeles) w/ 121 others. http://4sq.com/7rFgEf')
    print fourq_filter('I\'m at CVS/pharmacy in Northampton, MA http://gowal.la/c/2JBV9?137')
    print fourq_filter('Anddd go. (@ Sands Convention Center) http://4sq.com/aXyhBZ')
    print comma_filter('haha there is,  , a ,lot,,of coma,')
    print has_asianchar(u'我爱中国')
    print geo_rect((1,2), (2,3))
    print html_filter('<tag> &gt; some &lt; </tag> haha')

