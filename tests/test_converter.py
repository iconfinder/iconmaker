import os, sys, subprocess, unittest, tempfile
from struct import unpack
from PIL import Image
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from iconmaker import Converter, FORMAT_PNG, FORMAT_GIF, FORMAT_ICO, FORMAT_ICNS
from iconmaker.exceptions import ConversionError, ImageError


ICONS_TEST_DIR = os.path.join(os.path.dirname(
                                os.path.abspath(__file__)),
                                'icons')
RANDOM_ICONSETS = 20
LARGE_ICONSETS = 20

class ConverterTests(unittest.TestCase):
    """Unit tests for various conversion operations.
    """
    
    def setUp(self):
        self.converter = Converter()
    
    
    def assertAllTargetFormatsRaise(self, 
                                    exception, 
                                    files):
        """``convert`` calls with any target format raises the given exception.
        
        :param exception: Exception type.
        :param files: File list to pass to the convert class.
        """
        
        with self.assertRaises(Exception):
            self.converter.convert(files, 
                                   FORMAT_ICO, 
                                   tempfile.mkstemp('.ico')[1])
        with self.assertRaises(Exception):
            self.converter.convert(files, 
                                   FORMAT_ICNS, 
                                   tempfile.mkstemp('.icns')[1])
    
    
    def assertAllTargetFormatsSucceed(self,
                                      files):
        """``convert`` calls with any target format succeeds.

        :param files: File list to pass to the convert class.
        """

        for target_format, result_path in [(FORMAT_ICO, tempfile.mkstemp('.ico')[1], ), 
                                           (FORMAT_ICNS, tempfile.mkstemp('.icns')[1], )]:
            self.converter.convert(files, 
                                   target_format,
                                   result_path)
            self.assertTrue(os.path.exists(result_path))
            self.assertTrue(os.path.isfile(result_path))
            self.assertGreater(os.path.getsize(result_path), 0)

            # The one who created it has the final word whether
            # everything is OK
            if target_format == FORMAT_ICNS:
                self.assertTrue(subprocess.check_output([
                            self.converter.icns2png,
                            "-l",
                            result_path
                        ], stderr=subprocess.STDOUT))
            # simple check to see if it's ICO file
            # from http://en.wikipedia.org/wiki/ICO_(file_format)
            else:
                with open(result_path, 'rb') as f:
                    # header is 6 bytes
                    data = f.read(6)
                    fmt = '<3H' if sys.byteorder == 'little' else '>3H'
                    self.assertTrue(unpack(fmt, data))
                    header = unpack(fmt, data)
                    self.assertTrue(header[:2] == (0, 1))
    
    
    def test_convert_empty_image_list(self):
        """Test conversion from an empty source.
        """
        
        self.assertAllTargetFormatsRaise(ValueError, [])
    
    
    def test_convert_invalid_format(self):
        """Test conversion given an invalid target icon format.
        """
        
        with self.assertRaises(ConversionError):
            self.converter.convert('foo', [
                    os.path.join(ICONS_TEST_DIR, 'icon16x16.png'),
                    os.path.join(ICONS_TEST_DIR, 'icon32x32.png')
                ], 
                                   tempfile.mkstemp('.foo')[1])
    
    
    def test_convert_bad_local_pnglist(self):
        """Test conversion from bad local source.
        """
        
        self.assertAllTargetFormatsRaise(Exception, [
                os.path.join(ICONS_TEST_DIR, 'icon16x16.png'),
                os.path.join(ICONS_TEST_DIR, 'icon32x32.png'),
                '/foo.png'
            ])
    
    
    def test_convert_bad_remote_pnglist(self):
        """Test conversion from bad remote source.
        """
        
        self.assertAllTargetFormatsRaise(Exception, [
                'http://localhost:62010/www/icon16x16.png',
                'http://localhost:62010/www/foo.png',
                'http://localhost:62010/www/icon32x32.png'
            ])
    
    
    def test_convert_local(self):
        """Test conversion from local source.
        """
        
        # Test a simple conversion.
        self.assertAllTargetFormatsSucceed([
                os.path.join(ICONS_TEST_DIR, 'icon16x16.gif'),
                os.path.join(ICONS_TEST_DIR, 'icon32x32.png')
            ])

    def test_convert_remote(self):
        """Test conversion from remote source.
        """

        self.assertAllTargetFormatsSucceed([
                'http://cdn1.iconfinder.com/data/icons/yooicons_set01_socialbookmarks/16/social_facebook_box_blue.png', 
                'http://cdn1.iconfinder.com/data/icons/yooicons_set01_socialbookmarks/32/social_facebook_box_blue.png'
            ])

    def test_large_iconsets(self):
        """Test converting iconssets from the db (large)
        """

        #return

        import mysql.connector

        # connect to the db
        db = mysql.connector.Connect(host = os.getenv('DB_HOST', 'localhost'), 
                                     user = os.getenv('DB_USER', 'root'),
                                     password = os.getenv('DB_PASSWORD', ''),
                                     database = os.getenv('DB_DATABASE', 'www_iconfinder'))
        cursor = db.cursor()

        #
        # get large iconsets where there are atleast 8 size icons for each
        #

        sqlquery = """
SELECT
    i.name, i.iconid, i.newpath
FROM
    icondata i
INNER JOIN
    (
        SELECT
            iconid,
            count(size)
        FROM
            icondata
        WHERE
            active = 1 AND
            sizex IS NOT NULL AND
            sizey IS NOT NULL
        GROUP BY
            iconid
        HAVING
            count(distinct(size)) > 8
        LIMIT %s
    ) i2
ON i.iconid = i2.iconid
WHERE
    active = 1 AND
    sizex IS NOT NULL AND
    sizey IS NOT NULL
ORDER BY
    i.iconid, i.size""" % LARGE_ICONSETS

        cursor.execute(sqlquery)

        rows = cursor.fetchall()
        cursor.close()
        db.close()

        # create dict populated with
        #   key (collection name) -> values (list containing urls)
        iconsets = {}
        for row in rows:
            (name, iconid, newpath) = row
            iconsets.setdefault(
                name,
                []).append("http://cdn1.iconfinder.com/data/icons/%s%s" %
                    (newpath, name))

        # cycle through the collections and test them out
        for iconset in iconsets.values():
            self.assertAllTargetFormatsSucceed(iconset)

    def test_random_iconsets(self):
        """Test converting iconssets from the db (random)
        """

        #return

        # generate a list of icons to test
        import mysql.connector

        # pull up 100 icon sets, and generate ico/icns for them
        db = mysql.connector.Connect(host = os.getenv('DB_HOST', 'localhost'), 
                                     user = os.getenv('DB_USER', 'root'),
                                     password = os.getenv('DB_PASSWORD', ''),
                                     database = os.getenv('DB_DATABASE', 'www_iconfinder'))
        cursor = db.cursor()

        # get N random iconsets
        # using 1, 1000 inclusive for iconid
        import random
        random_iconsets = [random.randint(1, 1000) for r in
                            xrange(RANDOM_ICONSETS)]

        sql_query = """
SELECT
    name,
    iconid,
    newpath
FROM
    icondata
WHERE
    active = 1 AND
    sizex IS NOT NULL AND
    sizey IS NOT NULL AND
    iconid IN (%s)
ORDER BY
    iconid""" % ','.join([str(i) for i in random_iconsets])

        cursor.execute(sql_query)

        rows = cursor.fetchall()
        cursor.close()
        db.close()

        # create dict populated with
        #   key (collection name) -> values (list containing urls)
        iconsets = {}
        for row in rows:
            (name, iconid, newpath) = row
            iconsets.setdefault(
                name,
                []).append("http://cdn1.iconfinder.com/data/icons/%s%s" %
                    (newpath, name))

        # cycle through the collections and test them out
        for iconset in iconsets.values():
            self.assertAllTargetFormatsSucceed(iconset)
