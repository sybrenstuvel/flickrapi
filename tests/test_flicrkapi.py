#!/usr/bin/env python

'''Unittest for the FlickrAPI.

Far from complete, but it's a start.
'''

import unittest
import sys
import urllib
import StringIO

# Make sure the flickrapi module from the source distribution is used
sys.path.insert(0, '..')

import flickrapi

print "Testing FlickrAPI version %s %s" % (flickrapi.__version__, flickrapi.__revision__)

# Some useful constants
EURO_UNICODE = u'\u20ac'
EURO_UTF8 = EURO_UNICODE.encode('utf-8')
U_UML_UNICODE = u'\u00fc'
U_UML_UTF8 = U_UML_UNICODE.encode('utf-8')

key = '123key'
secret = '42'
f = flickrapi.FlickrAPI(key, secret)

class SigningTest(unittest.TestCase):
    '''Tests the signing of different arguments.'''

    def testSimple(self):
        '''Simple arguments, just ASCII'''
        
        signed = f.sign({'abc': 'def'})
        self.assertEqual('11b956a9182f533065157c0b08539fcf', signed)

        # Order shouldn't matter
        signed = f.sign({'abc': 'def', 'foo': 'bar'})
        self.assertEqual('ec0a50e52a86751c2effbf5c8f96d5e8', signed)

        signed = f.sign({'foo': 'bar', 'abc': 'def'})
        self.assertEqual('ec0a50e52a86751c2effbf5c8f96d5e8', signed)

    def testUnicode(self):
        '''Test signing of Unicode data'''

        # Unicode can't be signed directly
        self.assertRaises(flickrapi.IllegalArgumentException, f.sign, {'abc': u'def'})

        # But converted to UTF-8 works just fine
        signed = f.sign({'abc': u'def'.encode('utf-8')})
        self.assertEqual('11b956a9182f533065157c0b08539fcf', signed)
        
        # Non-ASCII data should work too
        data = EURO_UNICODE + U_UML_UNICODE
        signed = f.sign({'abc': data.encode('utf-8')})
        self.assertEqual('0f6e51fe5121a9713fb1ca383bb8551c', signed)

        # Straight UTF-8 should work too
        data = EURO_UTF8 + U_UML_UTF8
        signed = f.sign({'abc': data})
        self.assertEqual('0f6e51fe5121a9713fb1ca383bb8551c', signed)

class EncodingTest(unittest.TestCase):
    '''Test URL encoding + signing of data. Tests using sets, because
    we don't know in advance in which order the arguments will show up,
    and we don't care about that anyway.
    '''
    
    def testSimple(self): 
        '''Test simple ASCII-only data'''

        encoded = f.encode_and_sign({'abc': 'def', 'foo': 'bar'})
        expected = set(['abc=def',
                        'foo=bar',
                        'api_sig=ec0a50e52a86751c2effbf5c8f96d5e8'
                        ])
        self.assertEqual(expected, set(encoded.split('&')))

        # Order shouldn't matter for the signature
        encoded = f.encode_and_sign({'foo': 'bar', 'abc': 'def'})
        self.assertEqual(expected, set(encoded.split('&')))

    def testUnicode(self):
        '''Test Unicode data'''

        # Unicode strings with ASCII data only should result in the
        # same as in the testSimple() test. 
        encoded = f.encode_and_sign({'abc': u'def', 'foo': u'bar'})
        expected = set(['abc=def',
                        'foo=bar',
                        'api_sig=ec0a50e52a86751c2effbf5c8f96d5e8'
                        ])
        self.assertEqual(expected, set(encoded.split('&')))

        # Non-ASCII UTF-8 data should work too
        # EURO = 0xE2 0x82 0xAC in UTF-8
        # U_UML = 0xC3 0xBC in UTF-8
        data = EURO_UNICODE + U_UML_UNICODE
        encoded = f.encode_and_sign({'abc': data.encode('utf-8')})
        expected = set(['abc=%E2%82%AC%C3%BC',
                        'api_sig=0f6e51fe5121a9713fb1ca383bb8551c'
                        ])
        self.assertEqual(expected, set(encoded.split('&')))

        # Straight Unicode should work too
        data = EURO_UNICODE + U_UML_UNICODE
        encoded = f.encode_and_sign({'abc': data})
        self.assertEqual(expected, set(encoded.split('&')))

class DynamicMethodTest(unittest.TestCase):
    '''Tests the dynamic methods used to interface with Flickr.'''
    
    class FakeUrllib(object):
        '''Fake implementation of URLLib'''
    
        def __init__(self):
            self.data = None
            self.url = None
            
        def urlopen(self, url, postdata):
            self.url = url
            self.data = postdata
            
            return StringIO.StringIO('''<?xml version="1.0" encoding="utf-8"?>
                <rsp stat="ok"></rsp>''')

        def __getattr__(self, name):
            '''If we don't implement a method, call the original'''
            
            if not hasattr(urllib, name):
                raise AttributeError("No such attibute %s" % name)
            
            return getattr(urllib, name)
            
            #def original_caller(*args, **kwargs):
            #    original(*args, **kwargs)
            
    def setUp(self):
        # Set fake urllib
        self.fake_url_lib = self.FakeUrllib() 
        flickrapi.urllib = self.fake_url_lib

    def tearDown(self):
        # Restore original urllib
        flickrapi.urllib = urllib
    
    def testUnicodeArgs(self):
        '''Tests whether Unicode arguments are properly handled.
        
        Tests using sets, since the order of the URL-encoded arguments
        can't be ensured.
        '''
        
        # Plain ASCII should work
        f.photos_setMeta(monkey='lord')
        sent = set(self.fake_url_lib.data.split('&'))
        expected = set(['api_key=123key', 
                        'monkey=lord', 
                        'method=flickr.photos.setMeta', 
                        'api_sig=fc6e5f9532f3c3e4c8bfd86cf93884a0'
                        ])
        self.assertEquals(expected, sent)
         
        # Unicode should work too
        f.photos_setMeta(title='monkeylord',
                         description=EURO_UNICODE+U_UML_UNICODE)
        sent = set(self.fake_url_lib.data.split('&'))
        expected = set(['api_key=123key',
                        'title=monkeylord',
                        'description=%E2%82%AC%C3%BC',
                        'method=flickr.photos.setMeta',
                        'api_sig=ffde3c04d60f752ad5a1547dd9d8b4d6'
                        ])
        self.assertEquals(expected, sent)
         
        
if __name__ == '__main__':
    unittest.main()