import subprocess, os, tempfile, requests, struct

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
SUPPORTED_SIZES_ICNS = [16, 32, 48, 128, 256, 512, 1024]


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
        if not size_width in SUPPORTED_SIZES_ICNS:
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

    PNG2ICNS = '/usr/local/bin/png2icns'
    ICNS2PNG = '/usr/local/bin/icns2png'
    CONVERTTOOL = '/opt/local/bin/convert'
    """Cache image manipulation binary locations.
    """

    def __init__(self):
        """Initializer.
        """

        self.png2icns = ''
        self.icns2png = ''
        self.converttool = ''
        self.notices = []

        # check and/or find the correct file locations
        if not (os.path.isfile(Converter.PNG2ICNS)
            or os.access(Converter.PNG2ICNS, os.X_OK)):
            self.png2icns = which(os.path.basename(Converter.PNG2ICNS))
            if not self.png2icns:
                raise Exception("Unable to locate png2icns binary: %s" %
                    Converter.PNG2ICNS)
        else:
            self.png2icns = Converter.PNG2ICNS

        if not (os.path.isfile(Converter.ICNS2PNG)
            or os.access(Converter.ICNS2PNG, os.X_OK)):
            self.icns2png = which(os.path.basename(Converter.ICNS2PNG))
            if not self.icns2png:
                raise Exception("Unable to locate icns2png binary: %s" %
                    Converter.ICNS2PNG)
        else:
            self.icns2png = Converter.ICNS2PNG

        if not (os.path.isfile(Converter.CONVERTTOOL)
            or os.access(Converter.CONVERTTOOL, os.X_OK)):
            self.converttool = which(os.path.basename(Converter.CONVERTTOOL))
            if not self.converttool:
                raise Exception("Unable to locate image conversion tool: %s" %
                    Converter.CONVERTTOOL)
        else:
            self.converttool = Converter.CONVERTTOOL

    def fetch_image(self, url):
        """Fetch the requested image and save it in a temporary file.

        :params input: URL of the image to fetch.
        :returns:
            Path of the fetched image.
        """

        # Get the image.
        response = requests.get(url)
        response.raise_for_status(allow_redirects = False)

        # Save the image.
        im = Image.open(StringIO(response.content))
        image_format = im.format.lower()
        if image_format not in Converter.SUPPORTED_SOURCE_FORMATS:
            raise ImageError('The source file is not of a supported format.'
                'Supported formats are: %s' % (
                ', '.join(Converter.SUPPORTED_SOURCE_FORMATS)))

        # generate temp filename for it
        saved_file = tempfile.NamedTemporaryFile(
                        prefix='downloaded_',
                        suffix='.' + image_format,
                        delete=False)
        saved_filename = saved_file.name

        logging.debug('Fetching image to: %s' % (saved_filename))

        try:
            im.save(saved_filename)
        except:
            raise ImageError('Error saving image: %s' % (url))

        return saved_filename

    def verify_generated_icon(self,
                              target_format,
                              result_path):
        """Verify the target (ICO or ICNS) image.

        :param target_format: Target icon format.
        :param result_path: Path to the generated icon.

        :returns:
            ``True`` if it's a valid icon otherwise ``False``
        """
        # Simple check to see if it's a valid ICNS file
        # from http://en.wikipedia.org/wiki/Apple_Icon_Image_format
        if target_format == FORMAT_ICNS:
            with open(result_path, 'rb') as f:
                # parse header section (8 bytes)
                header = f.read(8)
                if len(header) != 8:
                    return False

                header_unpacked = struct.unpack('>4BI', header)
                header_type = ''.join([chr(i) for i in header_unpacked[0:4]])
                if header_type != 'icns' or header_unpacked[4] <= 0:
                    return False

                return True

        # Simple check to see if it's a valid ICO file
        # from http://en.wikipedia.org/wiki/ICO_(file_format)
        elif target_format == FORMAT_ICO:
            with open(result_path, 'rb') as f:
                header = f.read(6)
                if len(header) != 6:
                    return False

                header_unpacked = struct.unpack('<3H', header)
                if header_unpacked[:2] != (0, 1) or header_unpacked[2] <= 0:
                    return False

                return True

        return False

    def resize_image(self,
                     image_path,
                     image_width,
                     image_height,
                     transparency):
        """Resize image.

        :param image_path: Path to the source icon.
        :param image_width: Width of the icon.
        :param image_height: Height of the icon.
        :param image_format: Format of the icon.
        :param target_format: Target icon format.
        :param transparency: Whether to add transparency or not.

        :returns:
            Path to the resized image.
        """

        resized_file = tempfile.NamedTemporaryFile(
                    prefix='resized_',
                    suffix='.' + os.path.splitext(image_path)[1][1:],
                    delete=False)
        resized_path = resized_file.name

        # Adding transparency to make a square image
        if transparency:
            args_string = "%s %s -gravity center -background transparent " \
                            "-extent %dx%d %s" % (self.converttool,
                                        image_path,
                                        image_width,
                                        image_height,
                                        resized_path)
        # Resizing square image to the closest supported size
        else:
            args_string = "%s %s -resize %dx%d %s" % (
                                        self.converttool,
                                        image_path,
                                        image_width,
                                        image_height,
                                        resized_path)

        args = args_string.split()

        logging.debug('Conversion call arguments: %r' % (args))

        try:
            subprocess.check_output(args,
                                    stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            raise ConversionError('Failed to resize image %s' % (e.output))

        return resized_path

    def fix_image_size(self,
                       image_dict,
                       image_path,
                       image_width,
                       image_height,
                       target_format):
        """Fix image size to the specifications of the target container icon 
            format.

        :param image_dict: Dictionary of sizes and image path mappings.
        :param image_path: Path to the source icon.
        :param image_width: Width of the icon.
        :param image_height: Height of the icon.
        :param target_format: Target icon format.

        :returns:
            ``Tuple`` consisting of fixed image, new width, new size or 
            ``None`` if the would be fixed image already exists
        """

        image_path_orig = image_path
        if target_format == FORMAT_ICNS:
            # Ensure the image is square,
            # otherwise add transparency to smaller side
            if image_width != image_height:
                logging.debug('Non square icon: %d:%d -> %d:%d' % (
                    image_width, 
                    image_height, 
                    max(image_width, image_height), 
                    max(image_width, image_height)))

                image_width = image_height = max(image_width, image_height)

                # check if the corrected size doesn't already exist
                if not (image_width, image_height) in image_dict:
                    logging.debug('Resizing with transparency: %s' % (
                        image_path))

                    image_path = self.resize_image(image_path,
                                                   image_width,
                                                   image_height,
                                                   True)

            # Ensure the image is of supported sizes,
            # otherwise resize it.
            if image_width not in SUPPORTED_SIZES_ICNS:
                # get the closest supported size
                closest = min(enumerate(SUPPORTED_SIZES_ICNS),
                    key=lambda x: abs(x[1] - image_width))[1]

                logging.debug('Non supported size: '
                    '%d:%d -> %d:%d' % (
                    image_width,
                    image_height,
                    closest,
                    closest))

                image_width = image_height = closest

                # the corrected size doesn't already exist
                if not (image_width, image_height) in image_dict:
                    logging.debug('Resizing without transparency: %s' % (
                        image_path))

                    image_path = self.resize_image(image_path,
                                                   image_width,
                                                   image_height,
                                                   False)
        elif target_format == FORMAT_ICO:
            # Downscale but mantain aspect ratio.
            if image_width > 256 or image_height > 256:
                max_size = max(image_width, image_height)
                ratio = max_size / 256
                image_width = int(image_width / ratio)
                image_height = int(image_height / ratio)

                if not (image_width, image_height) in image_dict:
                    image_path = self.resize_image(image_path,
                                                   image_width,
                                                   image_height,
                                                   False)

        # Did we generate a new image?
        if image_path_orig == image_path:
            return None
        else:
            return (image_path, image_width, image_height)

    def convert_to_png32(self,
                         source_path,
                         target_path):
        """Convert a source image to a 32 bit PNG image.

        :param source_path: Path of the source image.
        :param target_path: Path of the target image.
        :raises ConversionError: if conversion fails.
        """

        logging.debug('Converting input image to 32-bit PNG: %s -> %s' % (
            source_path, target_path))
        # Perform the conversion.
        try:
            subprocess.check_output([
                    self.converttool,
                    source_path,
                    'png32:%s' % (target_path)
                ], stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            raise ConversionError('Failed to convert input file to 32-bit PNG: %s' % (
                e.output))

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
            raise ConversionError('invalid target format identifier: %s' % (
                target_format))

        if len(image_list) == 0:
            raise ValueError('image input list cannot be empty')

        # Make sure that all input files are stored locally and as PNGs.
        # image_list can contain either a local path or an http url
        local_image_list = []
        for image_location in image_list:
            if ((image_location.startswith("http:")) or
                (image_location.startswith("https:"))):

                # Skip invalid/corrupt URLs
                try:
                    image_location = self.fetch_image(image_location)
                except requests.exceptions.HTTPError, e:
                    err = 'Could not retrieve image: %s' % str(e)
                    self.notices.append(err)
                    logging.debug(err)
                    continue
                except ImageError, e:
                    err = 'Could not save image: %s' % str(e)
                    self.notices.append(err)
                    logging.debug(err)
                    continue

            # Check the extension to see if we'll need to convert something
            # else to PNG.
            image_base, image_extension = os.path.splitext(image_location)
            image_extension = image_extension[1:]

            if image_extension == FORMAT_GIF:
                logging.debug('converting input GIF image to 32-bit PNG: %s' % (
                    image_location))
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
        # If they don't, we do our best job of correcting the wrongly-sized icons
        image_dict = {}
        for image_path in image_list:
            sizes = Image.open(image_path).size
            if not sizes in image_dict:
                image_dict[sizes] = image_path

        image_list = []
        resized_images = {}
        for (image_size, image_path) in image_dict.iteritems():
            (image_width, image_height) = image_size

            if not is_size_convertible_to_icon(image_width,
                                               image_height,
                                               target_format):

                fixed_image_tuple = self.fix_image_size(image_dict,
                                                     image_path,
                                                     image_width,
                                                     image_height,
                                                     target_format)

                if fixed_image_tuple:
                    (resized_path, resized_width, resized_height) = fixed_image_tuple
                    if not (resized_width, resized_height) in resized_images:
                        resized_images[(resized_width, resized_height)] = resized_path
                        image_list.append(resized_path)

            else:
                image_list.append(image_path)

        # Execute conversion command.
        logging.debug('Target path: %r' % (target_path))
        logging.debug('Image list: %r' % (image_list))

        if target_format == FORMAT_ICNS:
            args = [self.png2icns, target_path] + image_list
        elif target_format == FORMAT_ICO:
            args = [self.converttool] + image_list + [target_path]

        logging.debug('Conversion call arguments: %r' % (args))
        logging.debug('Conversion call: %s' % (
            ' '.join(['"%s"' % (a) if ' ' in a else a for a in args])))

        # Verify libicns' bogus errors
        try:
            subprocess.check_output(args, 
                                    stderr = subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            if not self.verify_generated_icon(target_format, target_path):
                raise ConversionError('Failed to create container icon: %s: %s' % (
                    target_format, e.output))
