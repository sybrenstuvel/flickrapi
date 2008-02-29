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

key = 'ecd01ab8f00faf13e1f8801586e126fd'
secret = '2ee3f558fd79f292'
f = flickrapi.FlickrAPI(key, secret)

class SuperTest(unittest.TestCase):
    '''Superclass for unittests, provides useful methods.'''
    
    def assertUrl(self, protocol, host, path, query_arguments, actual_url):
        '''Asserts that the 'actual_url' matches the given parts.'''
            
        # Test the URL part by part
        (urltype, rest) = urllib.splittype(actual_url)
        self.assertEqual('http', urltype)
        
        (hostport, path) = urllib.splithost(rest)
        self.assertEqual(flickrapi.FlickrAPI.flickr_host, hostport)
        
        (path, query) = urllib.splitquery(path)
        self.assertEqual(flickrapi.FlickrAPI.flickr_auth_form, path)
        
        attrvalues = query.split('&')
        attribs = dict(av.split('=') for av in attrvalues)
        self.assertEqual(query_arguments, attribs)
    
class FlickrApiTest(SuperTest):
    
    def test_repr(self):
        r = repr(f)
        self.assertTrue('FlickrAPI' in r)
        self.assertTrue(key in r)

    def test_auth_url(self):
        '''Test the authentication URL generation'''
        
        args = dict(api_key=key, frob='frob', perms='read')
        args['api_sig'] = f.sign(args)
        
        url = f.auth_url(args['perms'], args['frob'])
        
        self.assertUrl('http', flickrapi.FlickrAPI.flickr_host, 
                       flickrapi.FlickrAPI.flickr_auth_form, args, 
                       url)
        
    def test_web_login_url(self):
        '''Test the web login URL.'''
        
        args = dict(api_key=key, perms='read')
        args['api_sig'] = f.sign(args)
        
        url = f.web_login_url(args['perms'])
        
        self.assertUrl('http', flickrapi.FlickrAPI.flickr_host,
                       flickrapi.FlickrAPI.flickr_auth_form, args,
                       url)
        
        
    def test_simple_search(self):
        '''Test simple Flickr search'''
        
        # We expect to be able to find kittens
        rst = f.photos_search(tags='kitten')
        self.assertTrue(rst.photos[0]['total'] > 0)

    def test_explicit_format(self):
        '''Test explicitly requesting a certain format'''
        
        xml = f.photos_search(tags='kitten', format='rest')
        self.assertTrue(isinstance(xml, basestring))
        
        # Try to parse it
        rst = flickrapi.XMLNode.parse(xml, False)
        self.assertTrue(rst.photos[0]['total'] > 0)
    
    def test_token_constructor(self):
        '''Test passing a token to the constructor'''
        
        token = '123-abc-def'
        
        # Pass the token
        flickr = flickrapi.FlickrAPI(key, secret, token=token)
        
        # It should be in the in-memory token cache now
        self.assertEqual(token, flickr.token_cache.token)
        
        # But not in the on-disk token cache
        self.assertNotEqual(token, flickrapi.TokenCache(key))
        
class SigningTest(unittest.TestCase):
    '''Tests the signing of different arguments.'''

    def testSimple(self):
        '''Simple arguments, just ASCII'''
        
        signed = f.sign({'abc': 'def'})
        self.assertEqual('9f215401af1a35e89da67a01be2333d2', signed)

        # Order shouldn't matter
        signed = f.sign({'abc': 'def', 'foo': 'bar'})
        self.assertEqual('57ca69551c24c9c9ce2e2b5c832e61af', signed)

        signed = f.sign({'foo': 'bar', 'abc': 'def'})
        self.assertEqual('57ca69551c24c9c9ce2e2b5c832e61af', signed)

    def testUnicode(self):
        '''Test signing of Unicode data'''

        # Unicode can't be signed directly
        self.assertRaises(flickrapi.IllegalArgumentException, f.sign, {'abc': u'def'})

        # But converted to UTF-8 works just fine
        signed = f.sign({'abc': u'def'.encode('utf-8')})
        self.assertEqual('9f215401af1a35e89da67a01be2333d2', signed)
        
        # Non-ASCII data should work too
        data = EURO_UNICODE + U_UML_UNICODE
        signed = f.sign({'abc': data.encode('utf-8')})
        self.assertEqual('51188be8b03d1ee892ade48631bfc0fd', signed)

        # Straight UTF-8 should work too
        data = EURO_UTF8 + U_UML_UTF8
        signed = f.sign({'abc': data})
        self.assertEqual('51188be8b03d1ee892ade48631bfc0fd', signed)

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
                        'api_sig=57ca69551c24c9c9ce2e2b5c832e61af'
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
                        'api_sig=57ca69551c24c9c9ce2e2b5c832e61af'
                        ])
        self.assertEqual(expected, set(encoded.split('&')))

        # Non-ASCII UTF-8 data should work too
        # EURO = 0xE2 0x82 0xAC in UTF-8
        # U_UML = 0xC3 0xBC in UTF-8
        data = EURO_UNICODE + U_UML_UNICODE
        encoded = f.encode_and_sign({'abc': data.encode('utf-8')})
        expected = set(['abc=%E2%82%AC%C3%BC',
                        'api_sig=51188be8b03d1ee892ade48631bfc0fd'
                        ])
        self.assertEqual(expected, set(encoded.split('&')))

        # Straight Unicode should work too
        data = EURO_UNICODE + U_UML_UNICODE
        encoded = f.encode_and_sign({'abc': data})
        self.assertEqual(expected, set(encoded.split('&')))

    def testNoSecret(self):
        
        no_secret = flickrapi.FlickrAPI(key)
        data = EURO_UNICODE + U_UML_UNICODE
        encoded = no_secret.encode_and_sign({'abc': data})
        self.assertEqual('abc=%E2%82%AC%C3%BC', encoded)

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
        expected = set(['api_key=%s' % key, 
                        'monkey=lord', 
                        'method=flickr.photos.setMeta', 
                        'api_sig=edb3c60b63becf1738e2cd8fcc42834a',
                        'format=rest'
                        ])
        self.assertEquals(expected, sent)
         
        # Unicode should work too
        f.photos_setMeta(title='monkeylord',
                         description=EURO_UNICODE+U_UML_UNICODE)
        sent = set(self.fake_url_lib.data.split('&'))
        expected = set(['api_key=%s' % key,
                        'title=monkeylord',
                        'description=%E2%82%AC%C3%BC',
                        'method=flickr.photos.setMeta',
                        'api_sig=29fa7705fc721fded172a1c113304871',
                        'format=rest'
                        ])
        self.assertEquals(expected, sent)

    def test_private_attribute(self):
        '''Tests that we get an AttributeError when accessing an attribute
        starting with __.
        '''
        
        self.assertRaises(AttributeError, f, '__get_photos')

    def test_get_dynamic_method(self):
        
        method = f.photos_setMeta
        self.assertTrue(callable(method))
        self.assertEquals('flickr.photos.setMeta', method.method)

        # Test that we can get it again - should come from the cache,
        # but no way to test that.        
        method = f.photos_setMeta
        self.assertTrue(callable(method))
        self.assertEquals('flickr.photos.setMeta', method.method)
        
        
        
class ClassMethodTest(unittest.TestCase):

    fail_rsp = flickrapi.XMLNode.parse(
        '''<rsp stat="fail">
            <err code='412' msg='Expected error, just testing' />
           </rsp>''')

    good_rsp = flickrapi.XMLNode.parse(
        '''<rsp stat="ok">
            <err code='433' msg='Not an error' />
           </rsp>''')

    def test_failure(self):
        self.assertRaises(flickrapi.FlickrError,
                          flickrapi.FlickrAPI.test_failure, self.fail_rsp)

        self.assertRaises(flickrapi.FlickrError,
                          flickrapi.FlickrAPI.test_failure,
                          self.fail_rsp, True)

        flickrapi.FlickrAPI.test_failure(self.fail_rsp, False)

    def test_get_rsp_error_code(self):
        code = flickrapi.FlickrAPI.get_rsp_error_code(self.fail_rsp)
        self.assertEqual(412, code)
        
        code = flickrapi.FlickrAPI.get_rsp_error_code(self.good_rsp)
        self.assertEqual(0, code)
    
    def test_get_rsp_error_msg(self):
        msg = flickrapi.FlickrAPI.get_rsp_error_msg(self.fail_rsp)
        self.assertEqual(u'Expected error, just testing', msg)

        msg = flickrapi.FlickrAPI.get_rsp_error_msg(self.good_rsp)
        self.assertEqual(u'Success', msg)

if __name__ == '__main__':
    unittest.main()
