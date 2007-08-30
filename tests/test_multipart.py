# -*- encoding: utf-8 -*-

'''Unittest for the flickrapi.multipart module'''


import unittest
import sys
import os

# Make sure the flickrapi module from the source distribution is used
sys.path.insert(0, '..')

import flickrapi.multipart as multipart

class PartTest(unittest.TestCase):
    def testSimplePart(self):
        p = multipart.Part({'name': 'title', 'purpose': 'test'}, "Little red kitty")
        expect = [
            'Content-Disposition: form-data; name="title"; purpose="test"',
            '',
            'Little red kitty'
        ]
        self.assertEquals(expect, p.render())

    def testContentType(self):
        p = multipart.Part({'name': 'title', 'purpose': 'test'}, "Little red kitty", "text/plain")
        expect = [
            'Content-Disposition: form-data; name="title"; purpose="test"',
            'Content-Type: text/plain',
            '',
            'Little red kitty'
        ]
        self.assertEquals(expect, p.render())

    def testUnicodePayload(self):
        p = multipart.Part({'name': 'title', 'purpose': 'test'}, u"Little red kitty ©")
        expect = [
            'Content-Disposition: form-data; name="title"; purpose="test"',
            '',
            'Little red kitty ©'
        ]
        self.assertEquals(expect, p.render())

    def testFile(self):
        testfile_name = "testfile"
        testfile_payload = "This is a file"

        # Create the file
        testfile = open(testfile_name, "w")
        testfile.write(testfile_payload)
        testfile.close()

        p = multipart.FilePart({'name': 'textfile'}, testfile_name, "text/embedded")
        expect = [
            'Content-Disposition: form-data; name="textfile"; filename="%s"' % testfile_name,
            'Content-Type: text/embedded',
            '',
            testfile_payload
        ]

        result = p.render()
        for index, line in enumerate(expect):
            self.assertEquals(line, result[index])

        os.unlink(testfile_name)

class MultipartTest(unittest.TestCase):

    def testSimple(self):
        m = multipart.Multipart()
        p = multipart.Part({'name': 'title', 'purpose': 'test'}, "Little red kitty")
        m.attach(p)
        lines = str(m).split('\r\n')

        self.assertEquals(m.header(), ('Content-Type', 'multipart/form-data; boundary=' + m.boundary))
        self.assertEquals(lines[0], '--' + m.boundary)
        self.assertEquals(lines[1], 'Content-Disposition: form-data; name="title"; purpose="test"')
        self.assertEquals(lines[2], '')
        self.assertEquals(lines[3], 'Little red kitty')
        self.assertEquals(lines[4], '--' + m.boundary + '--')

    def testAttach(self):
        m = multipart.Multipart()
        p = multipart.Part({'name': 'title', 'purpose': 'test'}, "Little red kitty")
        m.attach(p)

        self.assertEquals([p], m.parts)

    def testUnicode(self):
        m = multipart.Multipart()
        p = multipart.Part({'name': 'title', 'purpose': 'test'}, u"Little red kitty © Ünicode")
        m.attach(p)
        lines = str(m).split('\r\n')

        self.assertEquals(m.header(), ('Content-Type', 'multipart/form-data; boundary=' + m.boundary))
        self.assertEquals(lines[0], '--' + m.boundary)
        self.assertEquals(lines[1], 'Content-Disposition: form-data; name="title"; purpose="test"')
        self.assertEquals(lines[2], '')
        self.assertEquals(lines[3], 'Little red kitty © Ünicode')
        self.assertEquals(lines[4], '--' + m.boundary + '--')

        self.assertTrue(isinstance(str(m), str))

if __name__ == '__main__':
    unittest.main()
