# -*- encoding: utf-8 -*-

'''Unittest for the flickrapi.cache module'''

import unittest
import sys
import time

# Make sure the flickrapi module from the source distribution is used
sys.path.insert(0, '..')

import flickrapi

class TestCache(unittest.TestCase):
    def test_store_retrieve(self):
        cache = flickrapi.SimpleCache()
        key = 'abc'
        value = 'def'
        cache.set(key, value)
        self.assertEqual(value, cache.get(key))

    def test_expire(self):
        cache = flickrapi.SimpleCache(timeout=1)
        key = 'abc'
        cache.set(key, 'def')
        time.sleep(1.1)
        self.assertFalse(key in cache)

    def test_delete(self):
        cache = flickrapi.SimpleCache()
        key = 'abc'
        cache.set(key, 'def')
        cache.delete(key)
        self.assertFalse(key in cache)

    def test_max_entries(self):
        max_entries = 90
        cache = flickrapi.SimpleCache(max_entries=max_entries)

        for num in xrange(100):
            cache.set('key-%03d' % num, 'value')

        removed = float(max_entries) / cache.cull_frequency

        self.assertEqual(100 - removed, len(cache))
