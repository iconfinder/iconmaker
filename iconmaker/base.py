# -*- coding: utf-8 -*-

import subprocess
import os
import sys


# convert a set of PNG icons to either ICO or ICNS format
class Iconmaker(object):
	def __init__(self, pnglist):
		self.pnglist = pnglist
		self.png2icns = '/usr/local/bin/png2icns'

	def to_png(self):
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
		# TBD
		pass

	def to_icns(self):
		#input_files = ' '.join(self.pnglist)

		#output filename is the same as the input files
		output_file = self.pnglist[0].split('.')[0] + '.icns'
		print 'output_file: %s' % (output_file,)

		# execute shell command
		try:
			args = self.pnglist
			args.insert(0, output_file)
			args.insert(0, self.png2icns)
			retcode = subprocess.call(args)
			if retcode < 0:
				print >>sys.stderr, "Child was terminated by signal", -retcode
			else:
				print >>sys.stderr, "Child returned", retcode
		except OSError, e:
		    print >>sys.stderr, "Execution failed:", e