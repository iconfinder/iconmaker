#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Path hack.
sys.path.insert(0, os.path.abspath('..'))
from iconmaker.converter import Converter

ICONS_TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
RANDOM_ICONSETS = 50

class ConverterTests(unittest.TestCase):
    """Unit tests for various conversion operations.
    """

    def test_convert_empty_pnglist(self):
        """Test conversion from an empty source.
        """
        converter = Converter()
        self.assertRaises(Exception, converter.convert, 'ico', [])
        self.assertRaises(Exception, converter.convert, 'icns', [])

    def test_convert_wrong_format(self):
        """Test conversion given a wrong icon format.
        """
        converter = Converter()
        self.assertRaises(Exception, converter.convert, 'foo', [os.path.join(ICONS_TEST_DIR,'icon16x16.png'),
                                                                os.path.join(ICONS_TEST_DIR,'icon32x32.png')
                                                                ])

    def test_convert_bad_local_pnglist(self):
        """Test conversion from bad local source.
        """
        converter = Converter()
        self.assertRaises(Exception, converter.convert, 'ico', [os.path.join(ICONS_TEST_DIR,'icon16x16.png'),
                                                                os.path.join(ICONS_TEST_DIR,'icon32x32.png'),
                                                                '/foo.png'
                                                                ])

        self.assertRaises(Exception, converter.convert, 'icns',[os.path.join(ICONS_TEST_DIR,'icon16x16.png'),
                                                                os.path.join(ICONS_TEST_DIR,'icon32x32.png'),
                                                                '/foo.png'
                                                                ])

    def test_convert_bad_remote_pnglist(self):
        """Test conversion from bad remote source.
        """
        converter = Converter()
        self.assertRaises(Exception, converter.convert, 'ico', ['http://localhost/www/icon16x16.png',
                                                                'http://localhost/www/foo.png',                
                                                                'http://localhost/www/icon32x32.png'
                                                                ])
        self.assertRaises(Exception, converter.convert, 'icns', ['http://localhost/www/icon16x16.png',
                                                                 'http://localhost/www/foo.png',                
                                                                 'http://localhost/www/icon32x32.png'
                                                                ])
    def test_convert_local(self):
        """Test conversion from local source.
        """
        converter = Converter()
        self.assertTrue(converter.convert('ico',  [ os.path.join(ICONS_TEST_DIR,'icon16x16.gif'),
                                                    os.path.join(ICONS_TEST_DIR,'icon32x32.png')
                                                   ]))
        self.assertTrue(converter.convert('icns', [ os.path.join(ICONS_TEST_DIR,'icon16x16.gif'),
                                                    os.path.join(ICONS_TEST_DIR,'icon32x32.png')
                                                   ]))

    def test_convert_remote(self):
        """Test conversion from remote source.
        """     
        converter = Converter()
        self.assertTrue(converter.convert('ico', ['http://localhost/www/icon16x16.png',
                                                   'http://localhost/www/icon32x32.png'
                                                  ]))
        self.assertTrue(converter.convert('icns', ['http://localhost/www/icon16x16.png',
                                                   'http://localhost/www/icon32x32.png'
                                                   ]))

    def test_iconsets(self):
        """Test converting iconssets from the db
        """
        converter = Converter()

        # generate a list of icons to test
        import mysql.connector

        # pull up 100 icon sets, and generate ico/icns for them
        db = mysql.connector.Connect(host="localhost",
            user="root",
            password="",
            database="iconfinder_local")
        cursor = db.cursor()

        # get N random iconsets
        # using 1, 1000 inclusive for iconid
        import random
        random_iconsets = [random.randint(1,1000) for r in xrange(RANDOM_ICONSETS)]

        cursor.execute("SELECT name, iconid, newpath\
            FROM icondata_local\
            WHERE (active = 1 AND \
                sizex IS NOT NULL AND \
                sizey IS NOT NULL AND \
                iconid IN (%s)) \
            ORDER BY iconid" % ','.join([str(i) for i in random_iconsets]))

        rows = cursor.fetchall()
        cursor.close()
        db.close()

        # create dict populated with key (collection name) -> values (list containing urls)
        iconsets = {}
        for row in rows:
            (name, iconid, newpath) = row
            iconsets.setdefault(name, []).append("http://cdn1.iconfinder.com/data/icons/%s%s" % (newpath, name))
            #print row

        # cycle through the collections and test them out
        for iconset in iconsets.values():
            self.assertTrue(converter.convert('ico', iconset))
            self.assertTrue(converter.convert('icns', iconset))



if __name__=='__main__':
    unittest.main()