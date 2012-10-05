# -*- coding: utf-8 -*-

import subprocess
import os
import sys

import settings

# convert a set of PNG icons to either ICO or ICNS format
# input: a list of paths of PNG files
# output: path to the final ICO or ICNS file 
class Converter(object):
	def __init__(self, pnglist):
		self.pnglist = pnglist
		self.png2ico_binary = settings.png2ico_binary
		self.png2icns_binary = settings.png2icns_binary

	def writeintofilebuf(self):
		# TBD
	    #if path.startswith("http:"):
	    #    url = urllib.quote(url)
	    #    input = StringIO()
	    #    input.write(urllib.urlopen(url).read())
	    #    input.seek(0)
	    #else:
	    #    input = open(path).read()
	    pass

	def to_ico(self):
		# output filename is the same as the input files
		output_file = self.pnglist[0].split('.')[0] + '.ico'
		print 'output_file: %s' % (output_file,)

		# execute shell command
		try:
			args = self.pnglist
			args.insert(0, output_file)
			args.insert(0, self.png2ico_binary)
			retcode = subprocess.call(args)
			if retcode < 0:
				print >>sys.stderr, "Child was terminated by signal", -retcode
			else:
				print >>sys.stderr, "Child returned", retcode
		except OSError, e:
		    print >>sys.stderr, "Execution failed:", e

		return output_file

	def to_icns(self):
		# output filename is the same as the input files
		output_file = self.pnglist[0].split('.')[0] + '.icns'
		print 'output_file: %s' % (output_file,)

		# execute shell command
		# $ binary output_file input_file [input_file2 ...]
		try:
			args = self.pnglist
			args.insert(0, output_file)
			args.insert(0, self.png2icns_binary)
			retcode = subprocess.call(args)
			if retcode < 0:
				print >>sys.stderr, "Child was terminated by signal", -retcode
			else:
				print >>sys.stderr, "Child returned", retcode
		except OSError, e:
		    print >>sys.stderr, "Execution failed:", e

		return output_file

