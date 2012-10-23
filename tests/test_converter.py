import os, sys, subprocess, unittest, tempfile, random
from struct import unpack
from PIL import Image
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import mysql.connector

from iconmaker import Converter, FORMAT_PNG, FORMAT_GIF, FORMAT_ICO, FORMAT_ICNS
from iconmaker.exceptions import ConversionError, ImageError


ICONS_TEST_DIR = os.path.join(os.path.dirname(
                                os.path.abspath(__file__)),
                                'icons')
RANDOM_ICONSETS = 10
LARGE_ICONSETS = 10


class ConverterTests(unittest.TestCase):
    """Unit tests for various conversion operations.
    """

    def setUp(self):
        self.converter = Converter()

        # connect to the db
        self.db = mysql.connector.Connect(
            host = os.getenv('DB_HOST', 'localhost'),
            user = os.getenv('DB_USER', 'root'),
            password = os.getenv('DB_PASSWORD', ''),
            database = os.getenv('DB_DATABASE', 'www_iconfinder'))
        self.cursor = self.db.cursor()

    def tearDown(self):
        self.cursor.close()
        self.db.close()

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

            # deep icon validation (i.e., check the header values)
            self.assertTrue(self.converter.verify_generated_icon(target_format,
                result_path))

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

    def test_convert_bad_png(self):
        """Test conversion of a 'bad' png.
        """

        self.assertAllTargetFormatsSucceed([
                os.path.join(ICONS_TEST_DIR, 'bad.png')
            ])

    def test_convert_local(self):
        """Test conversion from local source.
        """

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

    def test_convert_MAS_iconset(self):
        """Test conversion of a complete MAS (Mac App Store) iconset.
        """

        self.assertAllTargetFormatsSucceed([
                os.path.join(ICONS_TEST_DIR, 'ttp/icon16x16.png'),
                os.path.join(ICONS_TEST_DIR, 'ttp/icon32x32.png'),
                os.path.join(ICONS_TEST_DIR, 'ttp/icon64x64.png'),
                os.path.join(ICONS_TEST_DIR, 'ttp/icon128x128.png'),
                os.path.join(ICONS_TEST_DIR, 'ttp/icon256x256.png'),
                os.path.join(ICONS_TEST_DIR, 'ttp/icon512x512.png'),
                os.path.join(ICONS_TEST_DIR, 'ttp/icon1024x1024.png'),
            ])

    def test_large_iconsets(self):
        """Test conversion of large iconssets from the db.
        """

        #return

        # Get large iconsets where there are atleast 8 size icons for each.
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
    i.iconid, i.size""" % (LARGE_ICONSETS,)

        self.cursor.execute(sqlquery)
        rows = self.cursor.fetchall()

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
        """Test conversion of random iconssets from the db.
        """

        #return

        # get N random iconsets
        # using 1, 1000 inclusive for iconid
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

        self.cursor.execute(sql_query)
        rows = self.cursor.fetchall()

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
