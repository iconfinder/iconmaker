import subprocess, os, tempfile, requests

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from utils import check_and_get_image_sizes, which, image_mode_to_bit_depth
from logger import logging
from exceptions import ConversionError, ImageError
from PIL import Image

FORMAT_PNG = 'png'
FORMAT_GIF = 'gif'
FORMAT_ICO = 'ico'
FORMAT_ICNS = 'icns'


def is_size_convertible_to_icon(size_width, 
                                size_height, 
                                target_format):
    """Check whether an image of a given size is convertible to an icon format.
    
    :param size_width: Width of the image.
    :param size_height: Height of the image.
    :param target_format: Target icon format.
    :returns: 
        ``True`` if the image can be converted to the given target icon format 
        otherwise ``False``.
    """
    
    # Sizes are constrainted by format.
    if target_format == FORMAT_ICO:
        # The dimensions of the icons must in the range of [1 ; 256].
        if ((size_width < 1) or 
            (size_width > 256) or 
            (size_height < 1) or 
            (size_height > 256)):
            return False
    elif target_format == FORMAT_ICNS:
        # ICNS requires quadratic input images.
        if size_width != size_height:
            return False
        
        # Apple's ICNS format supports only a subset of image sizes.
        if not size_width in [16, 32, 48, 128, 256, 512, 1024]:
            return False
    
    # We should be good.
    return True


class Converter(object):
    """Convert a set of PNG/GIF icons to either ICO or ICNS format.
    """
    
    SUPPORTED_SOURCE_FORMATS = [FORMAT_GIF, 
                                FORMAT_PNG]
    """Support source image formats.
    """
    
    
    SUPPORTED_TARGET_FORMATS = [FORMAT_ICO, 
                                FORMAT_ICNS]
    """Supported target icon container formats.
    """
    

    def _fetch_image(self, url):
        """Fetch the requested image and save it in a temporary file.

        :params input: URL of the image to fetch.
        :returns:
            temporary local file system path of the fetched image with an 
            extension reflecting the image format.
        """

        # Get the image.
        response = requests.get(url)
        response.raise_for_status(allow_redirects = False)

        # Save the image.
        im = Image.open(StringIO(response.content))
        image_format = im.format.lower()
        if image_format not in Converter.SUPPORTED_SOURCE_FORMATS:
            raise ImageError('The source file is not of a supported format. Supported formats are: %s' % (', '.join(Converter.SUPPORTED_SOURCE_FORMATS)))

        # generate temp filename for it
        saved_file = tempfile.NamedTemporaryFile(
                        prefix='downloaded_',
                        suffix='.' + image_format,
                        dir='/tmp',
                        delete=False)
        saved_filename = saved_file.name

        im.save(saved_filename)
        return saved_filename
    
    
    def convert_to_png32(self, 
                         source_path, 
                         target_path):
        """Convert a source image to a 32 bit PNG image.
    
        :param source_path: Path of the source image.
        :param target_path: Path of the target image.
        :raises ConversionError: if conversion fails.
        """
        
        # Perform the conversion.
        try:
            subprocess.check_output([
                    self.converttool,
                    source_path,
                    'png32:%s' % (target_path)
                ], stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            raise ConversionError('failed to convert input file to 32-bit PNG: %s' % (e.output))
    
    
    def __init__(self):
        """Initializer.
        """

        Converter.SUPPORTED_SOURCE_FORMATS = [FORMAT_GIF, FORMAT_PNG]
        Converter.SUPPORTED_TARGET_FORMATS = [FORMAT_ICO, FORMAT_ICNS]
        self.png2icns = '/usr/local/bin/png2icns'
        self.icns2png = '/usr/local/bin/icns2png'
        self.converttool = '/opt/local/bin/convert'

        # check and/or find the correct file locations
        if not os.path.isfile(self.png2icns):
            self.png2icns = which(os.path.basename(self.png2icns))
            if not self.png2icns:
                raise Exception("Unable to locate png2icns binary: %s" %
                    self.png2icns)

        if not os.path.isfile(self.icns2png):
            self.icns2png = which(os.path.basename(self.icns2png))
            if not self.icns2png:
                raise Exception("Unable to locate icns2png binary: %s" %
                    self.icns2png)

        if not os.path.isfile(self.converttool):
            self.converttool = which(os.path.basename(self.converttool))
            if not self.converttool:
                raise Exception("Unable to locate image conversion tool: %s" %
                    self.converttool)
    
    
    def convert(self, 
                image_list, 
                target_format, 
                target_path):
        """Convert a list of image files to an ico/icns file.
        
        :param image_list:
            List of image files to convert (either local paths or URLs).
        :param target_format:
            Target format. Must be one of ``FORMAT_ICO`` and ``FORMAT_ICNS``.
        :param target_path:
            Target path of the conversion.
        """

        # Validate the input arguments.
        if target_format not in Converter.SUPPORTED_TARGET_FORMATS:
            raise ConversionError('invalid target format identifier: %s' % (target_format))
        
        if len(image_list) == 0:
            raise ValueError('image input list cannot be empty')
        
        # Make sure that all input files are stored locally and as PNGs.
        # image_list can contain either a local path or an http url
        local_image_list = []
        for image_location in image_list:
            if ((image_location.startswith("http:")) or 
                (image_location.startswith("https:"))):
                image_location = self._fetch_image(image_location)
            
            # Check the extension to see if we'll need to convert something 
            # else to PNG.
            image_base, image_extension = os.path.splitext(image_location)
            image_extension = image_extension[1:]

            if image_extension == FORMAT_GIF:
                logging.debug('converting input GIF image to 32-bit PNG: %s' % (image_location))
                image_location_png = "%s.%s" % (image_base, FORMAT_PNG)
                self.convert_to_png32(image_location, 
                                      image_location_png)
                image_location = image_location_png

            local_image_list.append(image_location)
        
        # Validate the bit depth of each PNG file.
        image_list = []
        
        for image_path in local_image_list:
            # Skip past the image if the bit depth is greater than or equal to 
            # 24 bits, which we're certain that png2icns handles well.
            image = Image.open(image_path)
            image_bit_depth = image_mode_to_bit_depth(image.mode)
            
            if image_bit_depth >= 24:
                image_list.append(image_path)
                continue
            
            # Convert the PNG file to 32 bit if we're below 24 bit.
            deeper_file = tempfile.NamedTemporaryFile(
                prefix = 'deeper_',
                suffix = '.png', 
                delete = False)
            deeper_filename = deeper_file.name
            
            self.convert_to_png32(image_path, 
                                  deeper_filename)
            image_list.append(deeper_filename)
        
        # Ensure that all image files have sizes compatible with the output 
        # format.
        image_sizes = []
        
        for image_path in image_list:
            image = Image.open(image_path)
            
            if not is_size_convertible_to_icon(image.size[0], 
                                               image.size[1], 
                                               target_format):
                raise ImageError('size of image %s (%d x %d) is incompatible with target format FORMAT_%s' % \
                                     (image_path, 
                                      image.size[0], 
                                      image.size[1], 
                                      target_format.upper()))
            
            image_size_tuple = (image.size[0], image.size[1], )
            if image_size_tuple in image_sizes:
                raise ImageError('multiple images of size %d x %d supplied' % \
                                     (image.size[0], 
                                      image.size[1]))
            image_sizes.append(image_size_tuple)
        
        # Execute conversion command.
        logging.debug('Target path: %r' % (target_path))
        logging.debug('Image list: %r' % (image_list))
            
        if target_format == FORMAT_ICNS:
            args = [self.png2icns, 
                    target_path] + image_list
        elif target_format == FORMAT_ICO:
            args = [self.converttool] + image_list + [target_path]
        
        logging.debug('Conversion call arguments: %r' % (args))
        logging.debug('Conversion call: %s' % (' '.join(['"%s"' % (a) if ' ' in a else a for a in args])))
        
        try:
            subprocess.check_output(args, 
                                    stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            raise ConversionError('Failed to create container icon: %s' % (e.output))
