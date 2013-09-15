# -*- coding: utf-8 -*-

import unittest

from flickrapi import core

class TestFlickrapiCore(unittest.TestCase):
    def test_make_bytes(self):

        d = core.make_bytes({'ascii-key': 'ascii-value',
                             'nonascii-ključ': 'nonascii-вредност',
                             'integer value': 1431,
                             'float value': 4.32})

        keys = sorted(d.keys())
        self.assertEqual(keys, ['ascii-key',
                                'float value',
                                'integer value',
                                'nonascii-ključ'])
        self.assertEqual(d['ascii-key'], b'ascii-value')
        self.assertEqual(d['float value'], b'4.32')
        self.assertEqual(d['integer value'], b'1431')
        self.assertEqual(d['nonascii-ključ'],
             b'nonascii-\xd0\xb2\xd1\x80\xd0\xb5\xd0\xb4\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82')




if __name__ == '__main__':
    unittest.main()
