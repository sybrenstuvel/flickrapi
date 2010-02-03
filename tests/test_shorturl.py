#!/usr/bin/env python

import unittest

from flickrapi import shorturl

class ShortUrlTest(unittest.TestCase):
    '''Tests the shorturl module.'''

    def test_encoding(self):
        '''Test ID to Base58 encoding.'''

        self.assertEqual(shorturl.encode(u'4325695128'), u'7Afjsu')
        self.assertEqual(shorturl.encode(u'2811466321'), u'5hruZg')

    def test_decoding(self):
        '''Test Base58 to ID decoding.'''

        self.assertEqual(shorturl.decode(u'7Afjsu'), u'4325695128')
        self.assertEqual(shorturl.decode(u'5hruZg'), u'2811466321')

    def test_short_url(self):
        '''Test photo ID to short URL conversion.'''

        self.assertEqual(shorturl.url(u'4325695128'),
                u'http://flic.kr/p/7Afjsu')
        self.assertEqual(shorturl.url(u'2811466321'),
                u'http://flic.kr/p/5hruZg')
