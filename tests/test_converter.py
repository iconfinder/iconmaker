#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Path hack.
sys.path.insert(0, os.path.abspath('..'))
from iconmaker.converter import Converter

""" Test local data
"""
icons_local = ['/Users/iconfinder/Iconmaker/tests/icons/package_network16x16.png',
				'/Users/iconfinder/Iconmaker/tests/icons/package_network32x32.png',
				'/Users/iconfinder/Iconmaker/tests/icons/package_network48x48.png'
			  ]	

icons_local_bad = ['/foo.png',
				'/Users/iconfinder/Iconmaker/tests/icons/package_network32x32.png',
				'/Users/iconfinder/Iconmaker/tests/icons/package_network48x48.png'
			  ]				  

""" Test remote data
"""
icons_remote = [
				'http://localhost/www/icon16x16.png',
				'http://localhost/www/icon32x32.png',
				'http://localhost/www/icon48x48.png',
				]			 

icons_remote_bad = [
				'http://localhost/www/icon16x16.png',
				'http://localhost/www/icon32x32.png',
				'http://localhost/www/foo.png',
				]				


class ConverterTests(unittest.TestCase):
	"""Unit tests for various conversion operations
	"""
	def test_convert_bad_local_pnglist(self):
		"""Test generation given a bad local pnglist
		"""
		converter = Converter()
		self.assertFalse(converter.convert('ico', icons_local_bad))	

	def test_convert_bad_remote_pnglist(self):
		"""Test generation given a bad remote pnglist
		"""
		converter = Converter()
		self.assertFalse(converter.convert('ico', icons_remote_bad))

	def test_convert_empty_pnglist(self):
		"""Test generation given an empty pnglist
		"""
		converter = Converter()
		self.assertFalse(converter.convert('ico', []))

	def test_convert_wrong_format(self):
		"""Test generation given a wrong icon format
		"""
		converter = Converter()
		self.assertRaises(KeyError, converter.convert('foo', icons_local))

	def test_convert_ico_local(self):
		"""Test generation of ico file from local sources
		"""
		converter = Converter()
		self.assertTrue(converter.convert('ico', icons_local))

	def test_convert_ico_remote(self):
		"""Test generation of ico file from remote sources
		"""		
		converter = Converter()
		self.assertTrue(converter.convert('ico', icons_remote))

	def test_convert_icns_local(self):
		"""Test generation of icns file from local sources
		"""		
		converter = Converter()
		self.assertTrue(converter.convert('icns', icons_local))

	def test_convert_icns_remote(self):
		"""Test generation of icns file from remote sources
		"""		
		converter = Converter()
		self.assertTrue(converter.convert('icns', icons_remote))


if __name__=='__main__':
	unittest.main()