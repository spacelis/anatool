"""File: db.py
Description:
This module manages connections to databases
"""
__version__ = '0.1.0'
__author__ = 'SpaceLis'

import MySQLdb

GEOSTREAM = {'host':'localhost', \
            'user' :'root', \
            'passwd' : '', \
            'db' : 'geostream', \
            'charset' : 'utf8', \
            'use_unicode' : False}

GEOTWEET = {'host':'localhost', \
            'user' :'root', \
            'passwd' : '', \
            'unix_socket': '/tmp/mariadb.sock',
            'db' : 'geostream', \
            'charset' : 'utf8', \
            'use_unicode' : False}

#TODO add db_probe to make db operation easier
class ConnectionPool(object):
    """Keep a pool of connection for use"""
    def __init__(self):
        super(ConnectionPool, self).__init__()
        self.pool = dict()

    def get_conn(self, config):
        """Return the connection cached or instantiation a new one"""
        key = str(config)
        if not self.pool.has_key(key):
            self.pool[key] = MySQLdb.connect(**config)
        return self.pool[key]

    def get_cur(self, config):
        """Return the cursor from the connection"""
        key = str(config)
        if not self.pool.has_key(key):
            self.pool[key] = MySQLdb.connect(**config)
        return self.pool[key].cursor(MySQLdb.cursors.DictCursor)

    def __len__(self):
        return len(self.pool)

    def __del__(self):
        for conn in self.pool.itervalues():
            conn.commit()
            conn.close()

CONN_POOL = ConnectionPool()

