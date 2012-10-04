#!/usr/bin/python

from iconmaker.base import *

if __name__=='__main__':
	icons = [
				'/Users/iconfinder/Iconmaker/icons/package_network16x16.png',
				'/Users/iconfinder/Iconmaker/icons/package_network32x32.png',
				'/Users/iconfinder/Iconmaker/icons/package_network48x48.png',
			]

	# init with icons
	#print Iconmaker.msg
	im = Iconmaker(icons)

	# convert to ICNS
	im.to_icns()