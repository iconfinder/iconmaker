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

""" Test remote data
"""
icons_remote = [
				'http://localhost/www/icon16x16.png',
				'http://localhost/www/icon32x32.png',
				'http://localhost/www/icon48x48.png',
				]			 


class ConverterTests(unittest.TestCase):
	"""Unit tests for various conversion operations
	"""

	def test_convert_ico_local(self):
		"""Test generation of ico file from local sources"""
		converter = Converter()
		result = converter.convert('ico', icons_local)
		self.assertTrue(result)

	def test_convert_ico_remote(self):
		"""Test generation of ico file from remote sources"""		
		converter = Converter()
		result = converter.convert('ico', icons_remote)
		self.assertTrue(result)

	def test_convert_icns_local(self):
		"""Test generation of icns file from local sources"""		
		converter = Converter()
		result = converter.convert('icns', icons_local)
		self.assertTrue(result)

	def test_convert_icns_remote(self):
		"""Test generation of icns file from remote sources"""		
		converter = Converter()
		result = converter.convert('icns', icons_remote)
		self.assertTrue(result)


if __name__=='__main__':
	unittest.main()