# iconmaker

Tool for converting icons from GIF or PNG images to ICO or ICNS icon container formats.


## Usage

The `iconmaker` library provides a single class, `Converter` for dealing with conversions. Input files must be in either CompuServe GIF or PNG format.

## Installation

To install iconmaker, first install the required dependencies (in the exact order as shown below).

JasPer (enables full support for 256x256 and 512x512 32-bit icons with masks as alpha channels):

	$ wget http://www.ece.uvic.ca/~frodo/jasper/software/jasper-1.900.1.zip
	$ ./configure
	$ make
	$ sudo make install

icnslib (for png to icns conversion):

	$ wget http://sourceforge.net/projects/icns/files/latest/download?source=files
	$ ./configure
	$ make
	$ sudo make install

ImageMagick (for GIF to PNG and PNG to ICO conversion):

	$ wget http://www.imagemagick.org/download/ImageMagick.tar.gz
	$ ./configure
	$ make
	$ sudo make install

Then, install iconmaker itself:

    $ python setup.py install
