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
        """Private method: _fetch_png
            :params input: url of the image to fetch
            :returns: path to the saved_filename
        """

        response = requests.get(url)

        saved_file = tempfile.NamedTemporaryFile(prefix='downloaded_', suffix='.png', dir='/tmp', delete=False)
        saved_filename = saved_file.name

        try:
            im = Image.open(StringIO.StringIO(response.content))
            im.save(saved_filename)
            logging.debug("saving image to: %s" % saved_filename)
        except Exception, e:
            logging.debug("problem saving image: %s to %s" % (e, saved_filename))
            return None

        return saved_filename

    # initializer
    def __init__(self):
        """initializer"""

        """ cache the file locations
        """
        self.png2ico = '/usr/local/bin/png2ico'
        self.png2icns = '/usr/local/bin/png2icns'

        """if it doesn't exist at the path above, 
        do a path search to find it, or throw an exception
        """
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

        :returns: local path to the generated ico or None if an error occured        
        """

        logging.debug("--------------------\n")
        logging.debug("start: %s %s" % (target_format, png_list))

        conversion_binary = None
        try:
            conversion_binary = self.convert_binaries[target_format.upper()]
        except KeyError, e:
            logging.debug("invalid target format: %s" % e)
            return None

        logging.debug("conversion binary: %s" % conversion_binary)

        """Loop over the elements and determine if any/all of them are http
        if so, download the images and use these images as the new png list
        Note: if one of the files errors out, we abort the mission
        """
        new_pnglist = []
        for resource in png_list:
            if resource.startswith("http:") or resource.startswith("https:"):
                logging.debug("\n")
                logging.debug("Fetching PNG: %s" % resource)
                fetched_filename = self._fetch_png(resource)

                if fetched_filename:
                    logging.debug("Downloaded: %s" % fetched_filename)
                    new_pnglist.append(fetched_filename)
                else:
                    return None

        png_list = new_pnglist if new_pnglist else png_list

        if not png_list:
            logging.debug("Empty input PNG list")           
            return None

        output_file = tempfile.NamedTemporaryFile(prefix='output_', suffix='.%s' % target_format, dir='/tmp', delete=False)
        output_filename = output_file.name
        logging.debug("output_filename: %s" % output_filename)

        # execute shell command
        try:
            args = png_list
            args.insert(0, output_filename)
            args.insert(0, conversion_binary)
            retcode = subprocess.call(args)
            logging.debug("retcode: %s" % retcode)
            if retcode != 0:
                return None
        except OSError, e:
            logging.debug("Execution of conversion tool failed: %" % e)
            return None

        return output_filename