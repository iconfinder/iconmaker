# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import utils
import tempfile
import requests
import StringIO
from PIL import Image

from logger import logging

class Converter(object):
    """Convert a set of PNG icons to either ICO or ICNS format
    """

    def _fetch_png(self, url):
        """Fetch the requested image and save it in a temporary file

            :params input: url of the image to fetch
            :returns: path to the saved_filename
        """

        # get the image
        response = requests.get(url)

        # generate temp filename for it
        saved_file = tempfile.NamedTemporaryFile(prefix='downloaded_', suffix='.png', dir='/tmp', delete=False)
        saved_filename = saved_file.name

        # save the image
        im = Image.open(StringIO.StringIO(response.content))
        im.save(saved_filename)

        return saved_filename


    def __init__(self):
        """Initializer
        """

        # cache the file locations
        self.png2ico = '/usr/local/bin/png2ico'
        self.png2icns = '/usr/local/bin/png2icns'

        # check and/or find the correct file locations
        if not os.path.isfile(self.png2ico):
            self.png2ico = utils.which(os.path.basename(self.png2ico))
            if not self.png2ico:
                raise Exception("ERROR: png2ico binary not found")

        if not os.path.isfile(self.png2icns):
            self.png2icns = utils.which(os.path.basename(self.png2icns))
            if not self.png2icns:
                raise Exception("ERROR: png2icns binary not found")

        self.convert_binaries = {'ICO':self.png2ico, 'ICNS':self.png2icns}


    def convert(self, target_format, png_list):
        """Convert a list of png files to an ico file

        :param target_format: ico or icns
        :param pnglist: list of png files to convert (either local paths or URLs)

        :returns: local path to the generated ico or None if an error occured        
        """

        # check our input arguments
        try:
            conversion_binary = self.convert_binaries[target_format.upper()]
        except:
            raise Exception("ERROR: Invalid target format. Target format must be either ICO or ICNS.")

        try:
            assert len(png_list) > 0
        except:
            raise Exception("ERROR: Input PNG list cannot be empty.")

        # if any/all of the elements are http, let's create a new list insteads
        remote_png_list = []
        for resource in png_list:
            if resource.startswith("http:") or resource.startswith("https:"):
                try:
                    fetched_filename = self._fetch_png(resource)
                except:
                    raise Exception("ERROR: Problem fetching image.")

                remote_png_list.append(fetched_filename)

        # if we had to fetch images, use those instead, otherwise 
        # use the original list
        png_list = remote_png_list if remote_png_list else png_list

        # output file for the ICNS or ICO
        output_file = tempfile.NamedTemporaryFile(prefix='output_', suffix='.%s' % target_format, dir='/tmp', delete=False)
        output_filename = output_file.name

        # builds args for the conversion command
        args = png_list
        args.insert(0, output_filename)
        args.insert(0, conversion_binary)

        # execute conversion command
        try:
            retcode = subprocess.call(args)
            assert retcode == 0
        except (OSError, AssertionError) as e:
            raise Exception("ERROR: executing conversion program failed. %s" % e)

        return output_filename