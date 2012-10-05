#!/usr/bin/python

# This will go into unit tests for IconCoverter class
from iconmaker.converter import Converter

if __name__=='__main__':
	# local files (when the user manually uploads them)
	icons_local = ['/Users/iconfinder/Iconmaker/tests/icons/package_network16x16.png',
					'/Users/iconfinder/Iconmaker/tests/icons/package_network32x32.png',
					'/Users/iconfinder/Iconmaker/tests/icons/package_network48x48.png'
					]
	# remote files
	icons_remote = [
					'http://localhost/www/icon16x16.png',
					'http://localhost/www/icon32x32.png',
					'http://localhost/www/icon48x48.png',
					]

	# create the converter object with png icons
	im = Converter(icons_remote)

	# convert to ICNS
	outputfile = im.to_icns()

	# successfully converted
	print "output file: %s" % outputfile