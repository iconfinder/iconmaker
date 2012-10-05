#!/usr/bin/python

# This will go into unit tests for IconCoverter class
from iconmaker.converter import *

if __name__=='__main__':
	icons = ['/Users/iconfinder/Iconmaker/tests/icons/package_network16x16.png',
			'/Users/iconfinder/Iconmaker/tests/icons/package_network32x32.png',
			'/Users/iconfinder/Iconmaker/tests/icons/package_network48x48.png']

	# create the converter object with png icons
	im = Converter(icons)

	# convert to ICNS
	outputfile = im.to_icns()

	# successfully converted
	print outputfile