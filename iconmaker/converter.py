# -*- coding: utf-8 -*-

import subprocess
import os
import sys
#from urllib import urlretrieve
import utils
import tempfile
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Converter(object):
	"""Convert a set of PNG icons to either ICO or ICNS format
	"""

	"""Private method: _fetch_png
		:params input: url of the image to fetch
		:returns 
	"""
	def _fetch_png(self, url):
		import requests
		response = requests.get(url)

		import StringIO
		from PIL import Image
		try:
		    im = Image.open(StringIO.StringIO(response.content))
		    logging.debug("format: %s" % im.format)
		    im.verify()
		except Exception, e:
			logging.debug("Exception: %" % e)
			saved_filename = ''

		saved_file = tempfile.NamedTemporaryFile(prefix='downloaded_png_', suffix='.png', dir='/tmp', delete=False)
		saved_filename = saved_file.name
		logging.debug("saving image to: %s" % saved_filename)

		im.save(saved_filename)
		return saved_filename


	# initializer
	def __init__(self):
		"""initializer"""

		self.png2ico = '/usr/local/bin/png2ico'
		self.png2icns = '/usr/local/bin/png2icns'

		"""if it doesn't exist at the path above, do a path search to find it, or throw an exception"""
		if not os.path.isfile(self.png2ico):
			self.png2ico = utils.which(os.path.basename(self.png2ico))
			if not self.png2ico:
				raise Exception("Error: png2ico binary not found")

		if not os.path.isfile(self.png2icns):
			self.png2icns = utils.which(os.path.basename(self.png2icns))
			if not self.png2icns:
				raise Exception("Error: png2icns binary not found")

		self.convert_binaries = {'ICO':self.png2ico, 'ICNS':self.png2icns}


	def convert(self, target_format, png_list):
		"""Convert a list of png files to an ico file
		:param target_format: ico or icns
		:param pnglist: list of png files to convert (either local paths or URLs)

		:returns local path to the generated ico or None if an error occured		
		"""

		logging.debug("\nconvert(): %s %s" % (target_format, png_list))

		conversion_binary = None
		try:
			conversion_binary = self.convert_binaries[target_format.upper()]
		except KeyError, e:
			logging.debug("invalid target format: %s" % e)
			return None

		logging.debug("conversion binary: %s" % conversion_binary)

		new_pnglist = []
		for resource in png_list:
			if resource.startswith("http:") or resource.startswith("https:"):
				saved_filename = ''
				logging.debug("Fetching PNG: %s" % resource)

				saved_filename = self._fetch_png(resource)

				if saved_filename:
					logging.debug("Downloaded: %s" % saved_filename)
					new_pnglist.append(saved_filename)

		png_list = new_pnglist if new_pnglist else png_list

		if not png_list:
			logging.debug("Empty png list")			
			return None

		output_file = tempfile.NamedTemporaryFile(prefix='output_icon_', suffix='.ico', dir='/tmp', delete=False)
		output_filename = output_file.name
		logging.debug("output_filename: %s" % output_filename)

		# execute shell command
		try:
			args = png_list
			args.insert(0, output_filename)
			args.insert(0, conversion_binary)
			retcode = subprocess.call(args)
		except OSError, e:
		    logging.debug("Execution failed: %" % e)
		    return None

		return output_filename