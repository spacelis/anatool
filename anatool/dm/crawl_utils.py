"""Version 0.1.4
This module is used for data management
History:
    0.1.4 add place id generating function to retrieve
        place informatin and a function to import those
        places
    0.1.3 using MySQL for data storage
    0.1.2 using SQL for full JSON and Redis for crawling
          list
    0.1.1 add import methods

"""

import json, re, logging, fileinput, gzip, time, os, sys
import _mysql_exceptions
import traceback
from anatool.dm.log_helper import LogFunction
from anatool.dm.db import GEOTWEET, CONN_POOL
from anatool.analyze.dataset import loadrows
from anatool.analyze.text_util import get_tokens, html_filter

def named(name, ext):
    """rename the file if there is a file in the same name
    """
    #FIXME
    i = 15
    while os.path.exists(name + '{0}'.format(i) + ext):
        i += 1
    return name + '{0}.'.format(i) + ext


@LogFunction('Filtering POI')
def filter_poi(dst, srcs):
    """ Filter out the tweets with the place type of POI (JSON version)
    """
    fdst = open(dst, 'w+')
    k = 0
    i = 0
    try:
        for line in fileinput.input(srcs, openhook = fileinput.hook_compressed):
            i += 1
            try:
                status = json.loads(line)
                if status != None and \
                    status.has_key('place') and \
                    status['place'] != None:

                    if status['place'].has_key('type'):
                        if status['place']['type'] == 'poi':
                            fdst.writelines(line)
                            k += 1
                    elif status['place'].has_key('place_type'):
                        if status['place']['place_type'] == 'poi':
                            fdst.writelines(line)
                            k += 1
            except ValueError:
                print 'ValueError at line {0}'.format(i)
    except IOError:
        logging.warning('IOError')
    fdst.flush()
    fdst.close()
    logging.info('Filtering POI::{0} tweets of {1} are identified with POI.'\
            .format(k, i))
    logging.info('------------------------------------------')

@LogFunction('Importing Tweets')
def im_tweet(srcs):
    """ Import tweet from file to database.
    """

    # Connect to MySQL database
    cur = CONN_POOL.get_cur(GEOTWEET)
    i = 0
    k = 0
    for line in fileinput.input(srcs, openhook = fileinput.hook_compressed):
        try:
            tjson = json.loads(line)
            lat = tjson['place']['bounding_box'] \
                            ['coordinates'][0][0][1]
            lng = tjson['place']['bounding_box'] \
                            ['coordinates'][0][0][0]
            timestr = tjson['created_at']
            timestru = time.strptime(timestr, '%a %b %d %H:%M:%S +0000 %Y')
                                    #Wed Apr 14 18:51:32 +0000 2010
            timex = time.strftime('%Y-%m-%d %H:%M:%S', timestru)
            item = (tjson['id'], \
                    tjson['place']['id'], \
                    tjson['user']['id'], \
                    tjson['text'], \
                    lat, \
                    lng, \
                    timex)

            k += 1
            if len(get_tokens(tjson['text']))>0:
                cur.execute('INSERT INTO sample ( \
                        id, \
                        place_id, \
                        user_id, \
                        text, \
                        lat, \
                        lng, \
                        geo,\
                        created_at) \
                        VALUES(%s,%s,%s,%s,%s,%s,GeomFromText(\'POINT({0} {1})\'),%s)'.format(lat, lng), item)
            cur.execute('INSERT INTO tweet_json(id, json) VALUES(%s,%s)', (tjson['id'], line))
            i += 1
        except _mysql_exceptions.IntegrityError:
            print 'Import Tweets::Tweet ID {0} ignored for duplication.'\
                    .format(tjson['id'])
        except StandardError:
            print 'Fail at line {0}'.format(k)
    logging.info('Import Tweet::{0} out of {1} imported.'.format(i, k))
    logging.info('------------------------------------------')

@LogFunction('Importing places')
def im_place(srcs):
    """ Import places from file to database.
    """

    # Connect to MySQL database
    cur = CONN_POOL.get_cur(GEOTWEET)

    k, i = 0, 0
    fi = fileinput.FileInput(openhook = fileinput.hook_compressed)
    for line in fi.input(srcs):
        try:
            tjson = json.loads(line)
            k += 1
            lat = 0
            lng = 0
            if tjson['place_type']!='country':
                lat = tjson['bounding_box'] \
                                ['coordinates'][0][0][1]
                lng = tjson['bounding_box'] \
                                ['coordinates'][0][0][0]

                item = (tjson['id'], \
                        tjson['name'], \
                        tjson['place_type'], \
                        tjson['contained_within'][0]['id'], \
                        tjson['contained_within'][0]['name'], \
                        tjson['contained_within'][0]['place_type'], \
                        lat, \
                        lng, \
                        tjson['country_code'])
            else:
                item = (tjson['id'], \
                        tjson['name'], \
                        None,
                        None,
                        None,
                        None,
                        None,
                        tjson['country_code'])

            cur.execute('INSERT INTO place ( \
            `id`, \
            `name`, \
            `type`, \
            `superior_id`, \
            `superior_name`, \
            `superior_type`, \
            `lat`, \
            `lng`, \
            `country`, \
            `geo`) \
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,GeomFromText(\'Point({0} {1})\'))'.format(lat, lng), item)
            cur.execute('INSERT INTO place_json (id, json) VALUES(%s,%s)', (tjson['id'], line))
            i += 1
        except _mysql_exceptions.IntegrityError:
            print 'Import Places::Place ID {0} ignored for duplication.'.format(
                tjson['id'])
        except StandardError:
            logging.error('Fail at line {0}'.format(k))

    logging.info('Import Places::{0} out of {1} imported.'.format(i, k))
    logging.info('------------------------------------------')

@LogFunction('Importing places\' genre')
def im_place_genre(srcs):
    """Update the genre of a place"""
    cur = CONN_POOL.get_cur(GEOTWEET)
    k = 0

    fi = fileinput.FileInput(openhook = fileinput.hook_compressed)
    for line in fi.input(srcs):
        k += 1
        try:
            rst = json.loads(line)
            pid = rst['t_place_id']
            cur.execute(r'''insert into foursquare_json(id, json) values(%s,%s)''', (str(pid), json.dumps(rst['response']['groups'])))
        except _mysql_exceptions.IntegrityError:
            print 'Import place genre::Place {0} ignored for duplication.'\
                    .format(rst['t_place_id'])
        except StandardError as err:
            logging.error('Fail at line {0}, {1}'.format(k, err.message))
    CONN_POOL.get_conn(GEOTWEET).commit()

@LogFunction('Generating geocodes')
def gen_geocode_list(dst):
    """Generate geocode
    """
    fdst = open(dst, 'w')

    #cur = CONN_POOL.get_cur(GEOTWEET)
    #cur.execute('SELECT id, lat, lng, max_tweet_id\
            #FROM place_dist where cnt>100')
    i = 0
    for row in loadrows(GEOTWEET, ('id', 'lat', 'lng', 'max_tweet_id'), None, 'place_dist'):
        print >> fdst, '{0},{1},{2}${3}'.format( \
            row['lat'], row['lng'], '0.1km', row['max_tweet_id'])
        i += 1

    fdst.close()
    logging.info('Generate geocode::{0} geocodes are generated.'.format(i))
    logging.info('------------------------------------------')

@LogFunction('Generating user_id')
def gen_usr_list(dst):
    """Generate user list for crawling
    """
    fdst = open(dst, 'w')

    #cur = CONN_POOL.get_cur(GEOTWEET)
    #cur.execute('SELECT id, max_tweet_id\
            #FROM user_dist')
    i = 0
    for row in loadrows(GEOTWEET, ('id', 'max_tweet_id'), ('cnt>10',), 'user_dist'):
        print >> fdst, '{0}${1}'.format(row['id'], row['max_tweet_id'])
        i += 1

    fdst.close()
    logging.info('Generating user_id::{0} user IDs are generated.'.format(i))
    logging.info('------------------------------------------')

@LogFunction('Generating tweet_id')
def gen_twid_list(dst, srcs):
    """ Generate tweet ids that need to enrich.
    """
    fdst = open(dst, 'w+')

    cnt = 0
    for line in fileinput.input(srcs, openhook = fileinput.hook_compressed):
        try:
            status = json.loads(line)
            if status.has_key('place') and status['place'] != None:
                if status['place']['type'] != 'poi':
                    continue
                print >> fdst, status['id']
                cnt += 1
        except ValueError:
            print 'ValueError'

    fdst.flush()
    fdst.close()
    logging.info('Generate tweet_id ::{0} tweet IDs are generated.'.format(cnt))
    logging.info('------------------------------------------')

@LogFunction('Generating place_id')
def gen_poi_list(dst):
    """Generate POI list for crawling by POI id
    """
    fdst = open(dst, 'w')

    #cur = CONN_POOL.get_cur(GEOTWEET)
    #cur.execute('SELECT id, max_tweet_id FROM place_dist')
    i = 0
    for row in loadrows(GEOTWEET, ('id', 'max_tweet_id'), None, 'place_dist'):
        print >> fdst, '{0}${1}'.format(row['id'], row['max_tweet_id'])
        i += 1

    fdst.close()
    #cur.close()
    logging.info('Generate PID::{0} POI IDs are generated.'.format(i))
    logging.info('------------------------------------------')

@LogFunction('Generating place_name, coordinates')
def gen_place_info_list(dst):
    """Generate place name and coordinates for retrieving category
    """
    fdst = open(dst, 'w')


    #cur = CONN_POOL.get_cur(GEOTWEET)
    #cur.execute('SELECT id, name, lat, lng FROM place_dist WHERE category is NULL')
    i = 0
    for row in loadrows(GEOTWEET, ('id', 'name', 'lat', 'lng'), \
            None, 'place'):
        if row['name'] == None: continue
        print >> fdst, row['id'] + '$' \
                + row['name'] + '$' \
                + str(row['lat']) + ',' + str(row['lng'])
        i += 1

    fdst.close()
    #cur.close()
    logging.info('Generate place_name::{0} place are generated.'.format(i))
    logging.info('------------------------------------------')

@LogFunction('Filter data into sample')
def filter_tweet():
    """get rid of square game text"""
    scur = CONN_POOL.get_cur(GEOTWEET)
    dcur = CONN_POOL.get_cur(GEOTWEET)

    scur.execute('select id, text from tweet')
    i, k = 0, 0
    for tweet in scur:
        i += 1
        if len(get_tokens(tweet['text']))>0:
            dcur.execute('insert into `sample` \
                    select * from `tweet`\
                    where `tweet`.`id` = %s', tweet['id'])
            k += 1
    logging.info('{0} out of {1} tweets are transferred'.format(k, i))

@LogFunction('Merge two tweet file')
def merge_tweet(dst, srcs):
    """Merge the tweets in files into one file"""
    k, i = 0, 0
    idset = set()
    fdst = gzip.open(dst, 'wb')
    for line in fileinput.input(srcs, openhook = fileinput.hook_compressed):
        try:
            i += 1
            jtwt = json.loads(line)
            if jtwt['id'] not in idset:
                idset.add(jtwt['id'])
                print >>fdst, line.strip()
                print k, '\r',
                k += 1
        except Exception as e:
            pass
    print
    logging.info('{0} out of {1} merged'.format(k, i))

@LogFunction('Filter out pic URL')
def filter_picURL(dst, srcs):
    """Filter out all pic related URLs in tweets
    """
    from tcrawl.crawler import SERVICEPROVIDERS
    url_pattern = [re.compile('http://' + site + '/[a-zA-Z0-9_/-]+') \
            for site in SERVICEPROVIDERS.iterkeys()]
    hash_tag = re.compile('#[a-zA-z_]\\w*')

    fdst = open(dst, 'w')
    k, i = 0, 0
    for line in fileinput.input(srcs, openhook = fileinput.hook_compressed):
        try:
            i += 1
            jtwt = json.loads(line)
            if jtwt['text'].find('yfrog') > 0:
                ht = hash_tag.findall(jtwt['text'])
                if len(ht) == 0: continue
                for ptn in url_pattern:
                    mth = ptn.findall(jtwt['text'])
                    for url in mth:
                        urlpart = url.split('/')
                        print >> fdst, url + '$' \
                                + urlpart[2] + '_' + urlpart[-1] + '$'\
                                + str(jtwt['id']) + '$' \
                                + ','.join(ht)
                        k += 1
        except Exception:
            pass
    logging.info('{0} URLs out of {1} tweets'.format(k, i))

@LogFunction('New incoming data')
def process(srcs):
    """batch processing incoming data
    """
    poi_name = named('../data/poi_tmp', 'json')
    filter_poi(poi_name, srcs)
    im_tweet((poi_name,))
    mlist = ['../data/tweets.ljson.gz',]
    mlist.extend(srcs)
    merge_tweet('../data/tweets1.ljson.gz', mlist)

@LogFunction('Parse Bing search results')
def gen_urls(dst, srcs):
    """generate url to web pages list for crawling
    """
    fdst = open(dst, 'w')
    k = 0
    for line in fileinput.input(srcs, openhook = fileinput.hook_compressed):
        jlist = json.loads(line)
        for entry in jlist['gresults']:
            print >> fdst, u'$'.join((jlist['q'], entry['Url'])).encode('utf-8')
            k += 1
    print '{0} URLs generated'.format(k)
    fdst.close()


@LogFunction('Importing webpages')
def im_webpage(srcs):
    """ Import web pages from file to database.
    """
    # Connect to MySQL database
    cur = CONN_POOL.get_cur(GEOTWEET)
    i, k = 0, 0
    for line in fileinput.input(srcs, openhook = fileinput.hook_compressed):
        try:
            k += 1
            tjson = json.loads(line)
            item = (tjson['q'], \
                    html_filter(tjson['web']))
            cur.execute('INSERT INTO web ( \
                    place_id, \
                    web) \
                    VALUES(%s,%s)', item)
            i += 1
        except StandardError:
            print 'Fail at line {0}'.format(k)
            print traceback.print_exc(file=sys.stdout)
    logging.info('Import web pages::{0} out of {1} imported.'.format(i, k))
    logging.info('------------------------------------------')

if __name__ == '__main__':

    logging.basicConfig( \
        filename= '../../log/process.log', \
        level=logging.INFO, \
        format='%(asctime)s::%(levelname)s::%(message)s')
    CONSOLE = logging.StreamHandler()
    CONSOLE.setLevel(logging.INFO)
    logging.getLogger('').addHandler(CONSOLE)


    # running scripts
    #process(('../data/tweet-26_04_2011-17_29_29.ljson.gz',))
    #gen_urls('../data/list/web_rd1.lst', ('../data/websearch_b-28_04_2011-15_47_28.ljson',))
    #im_webpage(('../../data/web_f.ljson','../../data/web-06_05_2011-10_29_43.ljson.gz'))






    #filter_poi('../data/poi_rd15.ljson', \
            #('../data/tweet_g-15_04_2011-14_51_39.ljson.gz', ))
            #('../data/tweet_u-28_03_2011-15_39_49.ljson.gz',))
                #'../data/_tweets0.ljson',\
                #'../data/_tweets1.ljson'
                #))
    #im_tweet(('../data/tweet-15_04_2011-15_50_05.ljson.gz',))
    #im_place_genre(('../data/place_info-26_01_2011-13_56_44.ljson',))
            #'../data/place_info-10_01_2011-10_52_05.ljson'))
    #gen_sample('../data/somesample.json', '../db/geostream2.db', 10000)
    #gen_poi_list('../data/list/poi_list_r13.lst')
    #gen_geocode_list('../data/list/geocode_list_r16.lst')
    #gen_usr_list('../data/list/usr_r16.lst')
    #gen_twid_list('../data/list/en_list_r15.lst', ( \
            #'../data/poi_rd15.ljson',
            #'../data/tweet_g-03_03_2011-14_21_00.ljson',
            #'../data/tweet_g-31_03_2011-16_49_50.ljson.gz',
                    #))
    #gen_placeid_list('../data/place_list.lst')
    #im_place(('../data/place_info-31_01_2011-08_46_01.ljson',))
    #gen_place_info_list('../data/list/p_info_r13.lst')
    #filter_tweet()
    #merge_tweet('../data/tweets1.ljson.gz', \
            #('../data/tweets.ljson.gz', '../data/tweet_u-28_03_2011-15_39_49.ljson.gz',))
            #'../data/tweet_u-18_02_2011-13_36_39.ljson'))
    #filter_picURL('../data/list/pic_r4.lst',
            #(
                        #'../data/_tweets0.ljson',\
                        #'../data/_tweets1.ljson'
                #))
