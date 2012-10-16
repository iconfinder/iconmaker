IconMaker
=========

Tool for converting icons from gif/png to icns/ico formats.



Installation
------------

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

png2ico (for png to ico conversion):

	$ wget http://www.winterdrache.de/freeware/png2ico/data/png2ico-src-2002-12-08.tar.gz
	$ ./configure
	$ make
	$ sudo make install

ImageMagick (for gif to png conversion):

	$ wget http://www.imagemagick.org/download/ImageMagick.tar.gz
	$ ./configure
	$ make
	$ sudo make install

Then, install iconmaker itself:

    $ python setup.py install