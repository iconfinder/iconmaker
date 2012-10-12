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

FORMAT_PNG = 'png'
FORMAT_GIF = 'gif'
FORMAT_ICO = 'ico'
FORMAT_ICNS = 'icns'


class Converter(object):
    """Convert a set of PNG/GIF icons to either ICO or ICNS format.
    """

    def _fetch_image(self, url):
        """Fetch the requested image and save it in a temporary file.

            :params input: 
                URL of the image to fetch.
            :returns: 
                Path to the saved_filename.
        """

        # get the image
        response = requests.get(url)

        # save the image
        im = Image.open(StringIO.StringIO(response.content))
        image_format = im.format.lower()
        if image_format not in self.supported_source_formats:
            raise Exception('The source file is not of a supported format. Supported formats are: %s' % 
                            join(', ',self.supported_source_formats)) 

        # generate temp filename for it
        saved_file = tempfile.NamedTemporaryFile(prefix='downloaded_', suffix='.' + image_format, dir='/tmp', delete=False)
        saved_filename = saved_file.name            
        
        im.save(saved_filename)

        return saved_filename


    def __init__(self):
        """Initializer.
        """

        self.supported_source_formats = [FORMAT_GIF, FORMAT_PNG]
        self.supported_target_formats = [FORMAT_ICO, FORMAT_ICNS]
        self.png2ico = '/usr/local/bin/png2ico'
        self.png2icns = '/usr/local/bin/png2icns'
        self.gif2png = '/opt/local/bin/convert'

        # check and/or find the correct file locations
        if not os.path.isfile(self.png2ico):
            self.png2ico = utils.which(os.path.basename(self.png2ico))
            if not self.png2ico:
                raise Exception("The binary png2ico was not found")

        if not os.path.isfile(self.png2icns):
            self.png2icns = utils.which(os.path.basename(self.png2icns))
            if not self.png2icns:
                raise Exception("The binary png2icns was not found")

        if not os.path.isfile(self.gif2png):
            self.gif2png = utils.which(os.path.basename(self.gif2png))
            if not self.gif2png:
                raise Exception("The binary gif2png was not found")

        self.convert_binaries = {FORMAT_ICO:self.png2ico, FORMAT_ICNS:self.png2icns}


    def convert(self,
                target_format, 
                image_list):
        """Convert a list of image files to an ico/icns file.

        :param target_format: 
            ICO or ICNS.
        :param image_list: 
            List of image files to convert (either local paths or URLs).

        :returns: 
            Local path to the generated ico or None if an error occured.
        """


        # check our input arguments
        try:
            target_format = target_format.lower()
            conversion_binary = self.convert_binaries[target_format]
        except:
            raise Exception("Invalid target format. Target format must be either ICO or ICNS.")

        try:
            assert len(image_list) > 0
        except:
            raise Exception("Input list cannot be empty.")

        # if any/all of the elements are http, let's create a new list insteads
        remote_icon_list = []
        for resource in image_list:
            if resource.startswith("http:") or resource.startswith("https:"):
                try:
                    fetched_filename = self._fetch_image(resource)
                except:
                    raise Exception("Problem fetching image.")

                remote_icon_list.append(fetched_filename)

        # if we had to fetch images, use those instead, otherwise 
        # use the original list
        image_list = remote_icon_list if remote_icon_list else image_list

        # if the image is GIF, convert it to PNG first
        new_image_list = []
        for image_file_path in image_list:
            file_base, file_extension = os.path.splitext(image_file_path)
            file_extension = file_extension[1:]
            new_image_file_path = ''

            logging.debug('name, ext: %s %s' % (file_base, file_extension))

            if file_extension == FORMAT_GIF:
                logging.debug('converting %s' % image_file_path)
                new_image_file_path = file_base + '.' + FORMAT_PNG

                try:
                    retcode = subprocess.call([self.gif2png, image_file_path, new_image_file_path])
                    assert retcode == 0
                except:
                    raise Exception('GIF to PNG conversion failed. (%s)' % image_file_path)

            if new_image_file_path:
                new_image_list.append(new_image_file_path)
            else:
                new_image_list.append(image_file_path)

        image_list = new_image_list

        # output file in ICNS or ICO format
        output_file = tempfile.NamedTemporaryFile(prefix='output_', suffix='.%s' % target_format, dir='/tmp', delete=False)
        output_filename = output_file.name

        # builds args for the conversion command
        logging.debug('image list: %s' % image_list)
        args = image_list
        args.insert(0, output_filename)
        args.insert(0, conversion_binary)

        # execute conversion command
        try:
            retcode = subprocess.call(args)
            assert retcode == 0
        except:
            raise Exception("PNG to ICO/ICNS conversion failed. (%s)" % output_filename)

        return output_filename