#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Path hack.
sys.path.insert(0, os.path.abspath('..'))
from iconmaker.converter import Converter

icons_local = ['/Users/iconfinder/Iconmaker/tests/icons/package_network16x16.png',
				'/Users/iconfinder/Iconmaker/tests/icons/package_network32x32.png',
				'/Users/iconfinder/Iconmaker/tests/icons/package_network48x48.png'
			  ]	

icons_remote = [
				'http://localhost/www/icon16x16.png',
				'http://localhost/www/icon32x32.png',
				'http://localhost/www/icon48x48.png',
				]			 


class ConverterTests(unittest.TestCase):

	def test_convert_ico_local(self):
		im = Converter(icons_local)
		result = im.to_ico()
		self.assertTrue(result)

	def test_convert_ico_remote(self):
		im = Converter(icons_remote)
		result = im.to_ico()
		self.assertTrue(result)

	def test_convert_icns_local(self):
		im = Converter(icons_local)
		result = im.to_icns()
		self.assertTrue(result)

	def test_convert_icns_remote(self):
		im = Converter(icons_remote)
		result = im.to_icns()
		self.assertTrue(result)


if __name__=='__main__':
	unittest.main()