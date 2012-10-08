# -*- coding: utf-8 -*-

import subprocess
import os
import sys
from urllib import urlretrieve
#import requests
import utils

"""Convert a set of PNG icons to either ICO or ICNS format
input: a list of paths of PNG files
output: path to the final ICO or ICNS file"""
class Converter(object):
	# initializer
	def __init__(self, pnglist):
		self.pnglist = pnglist
		self.png2ico_binary = 'png2ico'
		self.png2icns_binary = 'png2icns'

		if not utils.which(self.png2ico_binary):
			raise Exception("Error: png2ico binary not found")

		if not utils.which(self.png2icns_binary):
			raise Exception("Error: png2icns binary not found")

		# download the files if the inputs are URLs
		newpnglist = []
		for resource in self.pnglist:
			if resource.startswith("http:") or resource.startswith("https:"):
				print "Fetching file: %s" % resource
				# todo: add error handling if there're problems fetching the file
				(filename, headers) = urlretrieve(resource)

				print "Downloaded: %s" % filename
				newpnglist.append(filename)

		if newpnglist:
			self.pnglist = newpnglist


	"""Convert a list of png files to an ico file"""
	def to_ico(self):
		if not self.pnglist:
			return None

		# output filename is the same as the input files
		output_file = self.pnglist[0].split('.')[0] + '.ico'
		print 'output_file: %s' % output_file

		# execute shell command
		try:
			args = self.pnglist
			args.insert(0, output_file)
			args.insert(0, self.png2ico_binary)
			retcode = subprocess.call(args)
		except OSError, e:
		    print "Execution failed:", e
		    return None

		return output_file


	"""Convert a list of png files to an icns file"""
	def to_icns(self):
		if not self.pnglist:
			return None

		# output filename is the same as the input files
		output_file = self.pnglist[0].split('.')[0] + '.icns'
		print 'output_file: %s' % output_file

		# execute shell command
		# $ binary output_file input_file [input_file2 ...]
		try:
			args = self.pnglist
			args.insert(0, output_file)
			args.insert(0, self.png2icns_binary)
			retcode = subprocess.call(args)
		except OSError, e:
			print "Execution failed: ", e
			return None

		return output_file