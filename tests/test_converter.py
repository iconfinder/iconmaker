#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Path hack.
sys.path.insert(0, os.path.abspath('..'))
from iconmaker.converter import Converter

ICONS_TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')

class ConverterTests(unittest.TestCase):
    """Unit tests for various conversion operations.
    """

    def test_convert_empty_pnglist(self):
        """Test generation given an empty pnglist.
        """
        converter = Converter()
        self.assertFalse(converter.convert('ico', []))
        self.assertFalse(converter.convert('icns', []))

    def test_convert_wrong_format(self):
        """Test generation given a wrong icon format.
        """
        converter = Converter()
        self.assertRaises(KeyError, converter.convert('foo', [  os.path.join(ICONS_TEST_DIR,'icon16x16.png'),
                                                                os.path.join(ICONS_TEST_DIR,'icon32x32.png')
                                                            ]))        

    def test_convert_bad_local_pnglist(self):
        """Test generation given a bad local pnglist.
        """
        converter = Converter()
        self.assertFalse(converter.convert('ico', [ os.path.join(ICONS_TEST_DIR,'icon16x16.png'),
                                                    os.path.join(ICONS_TEST_DIR,'icon32x32.png'),
                                                    '/foo.png',
                                            ])) 
        self.assertFalse(converter.convert('icns', [os.path.join(ICONS_TEST_DIR,'icon16x16.png'),
                                                    os.path.join(ICONS_TEST_DIR,'icon32x32.png'),
                                                    '/foo.png',
                                            ]))

    def test_convert_bad_remote_pnglist(self):
        """Test generation given a bad remote pnglist.
        """
        converter = Converter()
        self.assertFalse(converter.convert('ico', ['http://localhost/www/icon16x16.png',
                                                   'http://localhost/www/foo.png',                
                                                   'http://localhost/www/icon32x32.png',
                                            ]))
        self.assertFalse(converter.convert('icns', ['http://localhost/www/icon16x16.png',
                                                   'http://localhost/www/foo.png',                
                                                   'http://localhost/www/icon32x32.png',
                                            ]))

    def test_convert_local(self):
        """Test generation of ico file from local sources.
        """
        converter = Converter()
        self.assertTrue(converter.convert('ico', [  os.path.join(ICONS_TEST_DIR,'icon16x16.png'),
                                                    os.path.join(ICONS_TEST_DIR,'icon32x32.png')
                                                ]))
        self.assertTrue(converter.convert('icns', [  os.path.join(ICONS_TEST_DIR,'icon16x16.png'),
                                                    os.path.join(ICONS_TEST_DIR,'icon32x32.png')
                                                ]))

    def test_convert_remote(self):
        """Test generation of ico file from remote sources.
        """     
        converter = Converter()
        self.assertTrue(converter.convert('ico', ['http://localhost/www/icon16x16.png',
                                                   'http://localhost/www/icon32x32.png',
                                            ]))
        self.assertTrue(converter.convert('icns', ['http://localhost/www/icon16x16.png',
                                                   'http://localhost/www/icon32x32.png',
                                            ]))

if __name__=='__main__':
    unittest.main()