#!/usr/bin/env python

'''Unittest for the FlickrAPI.

Far from complete, but it's a start.
'''

import logging
import pkg_resources
import StringIO
import sys
import types
import unittest
import urllib
import urllib2
import webbrowser

# Make sure the flickrapi module from the source distribution is used
sys.path.insert(0, '..')

import flickrapi
flickrapi.set_log_level(logging.FATAL)
#flickrapi.set_log_level(logging.DEBUG)

print "Testing FlickrAPI version %s" % flickrapi.__version__

# Some useful constants
EURO_UNICODE = u'\u20ac'
EURO_UTF8 = EURO_UNICODE.encode('utf-8')
U_UML_UNICODE = u'\u00fc'
U_UML_UTF8 = U_UML_UNICODE.encode('utf-8')

key = 'ecd01ab8f00faf13e1f8801586e126fd'
secret = '2ee3f558fd79f292'

logging.basicConfig()
LOG = logging.getLogger(__name__)

def etree_package():
    '''Returns the name of the ElementTree package for the given
    Python version.'''

    current_version = sys.version_info[0:3]
    if current_version < (2, 5, 0):
        # For Python 2.4 and earlier, we assume ElementTree was
        # downloaded and installed from pypi.
        return 'elementtree.ElementTree'

    return 'xml.etree.ElementTree'

class SuperTest(unittest.TestCase):
    '''Superclass for unittests, provides useful methods.'''
    
    def setUp(self):
        super(SuperTest, self).setUp()
        self.f = flickrapi.FlickrAPI(key, secret)
        self.f_noauth = flickrapi.FlickrAPI(key)

        # Remove/prevent any unwanted tokens
        self.f.token_cache.forget()
        self.f_noauth.token_cache = flickrapi.tokencache.SimpleTokenCache()

    def print_auth_message(self, frob, perms):
        sys.stderr.write("Your browser starts, press ENTER after "
                "authentication")
        return self.f.validate_frob(frob, perms)

    def assertUrl(self, expected_protocol, expected_host, expected_path,
                  expected_query_arguments, actual_url):
        '''Asserts that the 'actual_url' matches the given parts.'''
            
        # Test the URL part by part
        (urltype, rest) = urllib.splittype(actual_url)
        self.assertEqual(expected_protocol, urltype)
        
        (hostport, path) = urllib.splithost(rest)
        self.assertEqual(expected_host, hostport)
        
        (path, query) = urllib.splitquery(path)
        self.assertEqual(expected_path, path)
        
        attrvalues = query.split('&')
        attribs = dict(av.split('=') for av in attrvalues)
        self.assertEqual(expected_query_arguments, attribs)
    
class FlickrApiTest(SuperTest):
    def test_repr(self):
        '''Class name and API key should be in repr output'''

        r = repr(self.f)
        self.assertTrue('FlickrAPI' in r)
        self.assertTrue(key in r)

    def test_auth_url(self):
        '''Test the authentication URL generation'''
        
        args = dict(api_key=key, frob='frob', perms='read')
        args['api_sig'] = self.f.sign(args)
        
        url = self.f.auth_url(args['perms'], args['frob'])
        
        self.assertUrl('http', flickrapi.FlickrAPI.flickr_host, 
                       flickrapi.FlickrAPI.flickr_auth_form, args, 
                       url)

    def test_auth_callback(self):
        '''Test auth_callback argument in get_token_part_one().'''

        # make sure this test is made without a valid token in the cache        
        self.f.token_cache.forget()

        test = {'called': False,
                'frob': None}

        def callback(frob, perms):
            test['called'] = True
            test['frob'] = frob

            self.assertEqual(perms, 'delete')
            self.assertTrue(frob, 'Expected to get a frob')

        (token, frob) = self.f.get_token_part_one(perms="delete",
                auth_callback=callback)

        # The token shouldn't be set
        self.assertEqual(None, token, "Expected token to be None")

        # The callback function should have been called
        self.assertTrue(test['called'],
                        'Expected callback function to be called')
        self.assertEqual(frob, test['frob'],
            'Expected same frob returned and passed in callback')

    def test_auth_callback_false(self):
        '''Test auth_callback argument in get_token_part_one().'''

        # make sure this test is made without a valid token in the cache        
        self.f.token_cache.forget()

        try:
            # Prevent the webbrowser module from being called.
            del flickrapi.webbrowser

            # Check that an exception is raised.
            self.assertRaises(flickrapi.FlickrError, self.f.get_token_part_one,
                    perms="read", auth_callback=False)
        finally:
            flickrapi.webbrowser = webbrowser

    def test_auth_callback_invalid(self):
        '''Test auth_callback argument in get_token_part_one().'''

        self.assertRaises(ValueError, self.f.get_token_part_one,
                perms="read", auth_callback='cookie')

    def test_web_login_url(self):
        '''Test the web login URL.'''
        
        args = dict(api_key=key, perms='read')
        args['api_sig'] = self.f.sign(args)
        
        url = self.f.web_login_url(args['perms'])
        
        self.assertUrl('http', flickrapi.FlickrAPI.flickr_host,
                       flickrapi.FlickrAPI.flickr_auth_form, args,
                       url)
        
    def test_simple_search(self):
        '''Test simple Flickr search'''
        
        # We expect to be able to find kittens
        result = self.f.photos_search(tags='kitten')
        total = int(result.find('photos').attrib['total'])
        self.assertTrue(total > 0)
    
    def test_token_constructor(self):
        '''Test passing a token to the constructor'''
        
        token = '123-abc-def'
        
        # Pass the token
        flickr = flickrapi.FlickrAPI(key, secret, token=token)
        
        # It should be in the in-memory token cache now
        self.assertEqual(token, flickr.token_cache.token)
        
        # But not in the on-disk token cache
        self.assertNotEqual(token, flickrapi.TokenCache(key))              

    def test_auth_token_without_secret(self):
        '''Auth tokens without secrets are meaningless'''

        
        token = '123-abc-def'
        
        # Create a normal FlickrAPI object
        flickr = flickrapi.FlickrAPI(key)

        flickr.token_cache.token = token
        self.assertRaises(ValueError, flickr.photos_search,
                          tags='kitten')

    def test_upload_without_filename(self):
        '''Uploading a file without filename is impossible'''
        
        self.assertRaises(flickrapi.IllegalArgumentException,
                          self.f.upload, '')
        
        self.assertRaises(flickrapi.IllegalArgumentException,
                          self.f.upload, None)

    def test_upload(self):
        photo = pkg_resources.resource_filename(__name__, 'photo.jpg')

        self.f.token_cache.username = 'unittest-upload'
        self.f.authenticate_console('delete', self.print_auth_message)
        result = self.f.upload(photo, is_public='0', content_type='2')

        # Now remove the photo from the stream again
        photo_id = result.find('photoid').text
        self.f.photos_delete(photo_id=photo_id)

    def test_cancel_upload(self):
        photo = pkg_resources.resource_filename(__name__, 'photo.jpg')

        self.f.token_cache.username = 'unittest-upload'
        self.f.authenticate_console('delete', self.print_auth_message)

        def callback(progress, done):
            '''Callback that immediately cancels the upload'''
            raise flickrapi.CancelUpload()

        try:
            self.f.upload(photo, callback=callback,
                is_public='0', content_type='2')
            self.fail("Expected exception not thrown")
        except flickrapi.CancelUpload, e:
            pass # Expected

    def test_store_token(self):
        '''Tests that store_token=False FlickrAPI uses SimpleTokenCache'''

        token_disk = '123-abc-disk'
        token_mem = '123-abc-mem'

        # Create a non-public-only instance, and set the on-disk token
        flickr = flickrapi.FlickrAPI(key, secret)
        flickr.token_cache.token = token_disk
        
        flickr = flickrapi.FlickrAPI(key, secret, store_token=False)

        # The token shouldn't be set
        self.assertEqual(None, flickr.token_cache.token)

        # Now set it
        flickr.token_cache.token = token_mem
        
        # It should not be in the on-disk token cache, only in memory
        self.assertEqual(token_disk, flickrapi.TokenCache(key).token)
        self.assertNotEqual(token_mem, flickrapi.TokenCache(key).token)

    def test_wrap_in_parser(self):
        '''Tests wrap_in_parser'''

        test = {'wrapped': False}

        def to_wrap(format, test_param):
            self.assertEqual('rest', format)
            self.assertEqual('test_value', test_param)
            test['wrapped'] = True

            return '<rst stat="ok"><element photo_id="5" /></rst>'

        rst = self.f._FlickrAPI__wrap_in_parser(to_wrap, parse_format='xmlnode',
                format='xmlnode', test_param='test_value')
        self.assertEqual('5', rst.element[0]['photo_id'])
        self.assertTrue(test['wrapped'],
                        'Expected wrapped function to be called')

    def test_wrap_in_parser_no_format(self):
        '''Tests wrap_in_parser without a format in the wrapped arguments'''

        test = {'wrapped': False}

        def to_wrap(test_param):
            self.assertEqual('test_value', test_param)
            test['wrapped'] = True

            return '<rst stat="ok"><element photo_id="5" /></rst>'

        rst = self.f._FlickrAPI__wrap_in_parser(to_wrap, parse_format='xmlnode',
                test_param='test_value')
        self.assertEqual('5', rst.element[0]['photo_id'])
        self.assertTrue(test['wrapped'],
                        'Expected wrapped function to be called')

class CachingTest(SuperTest):
    '''Tests that the caching framework works'''

    def test_cache_write(self):
        '''tests that the call result is written to cache'''

        photo_id = '2333478006'
        cache_key = ('api_key=%s'
                     '&photo_id=%s'
                     '&method=flickr.photos.getInfo'
                     '&format=rest' % (key, photo_id))
        
        f = flickrapi.FlickrAPI(key, store_token=False, format='rest')
        f.cache = flickrapi.SimpleCache()
        self.assertEqual(0, len(f.cache))

        info = f.photos_getInfo(photo_id=photo_id)

        self.assertEqual(info, f.cache.get(cache_key))

    def test_cache_read(self):
        '''Tests that cached data is returned if available'''

        photo_id = '2333478006'
        cache_key = ('api_key=%s'
                     '&photo_id=%s'
                     '&method=flickr.photos.getInfo'
                     '&format=rest' % (key, photo_id))
        faked_value = "FAKED_VALUE"
        
        f = flickrapi.FlickrAPI(key, store_token=False, format='rest')
        f.cache = flickrapi.SimpleCache()
        f.cache.set(cache_key, faked_value)

        info = f.photos_getInfo(photo_id=photo_id)

        self.assertEqual(faked_value, info)

    def test_cache_constructor_parameter(self):
        '''Tests that a cache is created when requested.'''

        f = flickrapi.FlickrAPI(key, cache=True)
        self.assertNotEqual(None, f.cache, "Cache should not be None")

    # Test list of non-cacheable method calls

class FormatsTest(SuperTest):
    '''Tests the different parsed formats.'''

    def test_default_format(self):
        '''Test that the default format is etree'''

        f = flickrapi.FlickrAPI(key)
        etree = f.photos_getInfo(photo_id=u'2333478006')
        self.assertEqual(etree_package(), etree.__module__)

    def test_etree_format_happy(self):
        '''Test ETree format'''

        etree = self.f_noauth.photos_getInfo(photo_id=u'2333478006',
                    format='etree')
        self.assertEqual(etree_package(), etree.__module__)

    def test_etree_format_error(self):
        '''Test ETree format in error conditions'''
 
        self.assertRaises(flickrapi.exceptions.FlickrError,
                self.f_noauth.photos_getInfo, format='etree')

    def test_etree_default_format(self):
        '''Test setting the default format to etree'''

        f = flickrapi.FlickrAPI(key, format='etree')
        etree = f.photos_getInfo(photo_id=u'2333478006')
        self.assertEqual(etree_package(), etree.__module__)

    def test_xmlnode_format(self):
        '''Test XMLNode format'''

        node = self.f_noauth.photos_getInfo(photo_id=u'2333478006',
                    format='xmlnode')
        self.assertNotEqual(None, node.photo[0])

    def test_xmlnode_format_error(self):
        '''Test XMLNode format in error conditions'''
 
        self.assertRaises(flickrapi.exceptions.FlickrError,
                self.f_noauth.photos_getInfo, format='xmlnode')
        
    def test_explicit_format(self):
        '''Test explicitly requesting a certain unparsed format'''
        
        xml = self.f.photos_search(tags='kitten', format='rest')
        self.assertTrue(isinstance(xml, basestring))
        
        # Try to parse it
        rst = flickrapi.XMLNode.parse(xml, False)
        self.assertTrue(int(rst.photos[0]['total']) > 0)

class SigningTest(SuperTest):
    '''Tests the signing of different arguments.'''

    def testSimple(self):
        '''Simple arguments, just ASCII'''
        
        signed = self.f.sign({'abc': 'def'})
        self.assertEqual('9f215401af1a35e89da67a01be2333d2', signed)

        # Order shouldn't matter
        signed = self.f.sign({'abc': 'def', 'foo': 'bar'})
        self.assertEqual('57ca69551c24c9c9ce2e2b5c832e61af', signed)

        signed = self.f.sign({'foo': 'bar', 'abc': 'def'})
        self.assertEqual('57ca69551c24c9c9ce2e2b5c832e61af', signed)

    def testUnicode(self):
        '''Test signing of Unicode data'''

        # Unicode can't be signed directly
        self.assertRaises(flickrapi.IllegalArgumentException, self.f.sign, {'abc': u'def'})

        # But converted to UTF-8 works just fine
        signed = self.f.sign({'abc': u'def'.encode('utf-8')})
        self.assertEqual('9f215401af1a35e89da67a01be2333d2', signed)
        
        # Non-ASCII data should work too
        data = EURO_UNICODE + U_UML_UNICODE
        signed = self.f.sign({'abc': data.encode('utf-8')})
        self.assertEqual('51188be8b03d1ee892ade48631bfc0fd', signed)

        # Straight UTF-8 should work too
        data = EURO_UTF8 + U_UML_UTF8
        signed = self.f.sign({'abc': data})
        self.assertEqual('51188be8b03d1ee892ade48631bfc0fd', signed)

class EncodingTest(SuperTest):
    '''Test URL encoding + signing of data. Tests using sets, because
    we don't know in advance in which order the arguments will show up,
    and we don't care about that anyway.
    '''
    
    def testSimple(self): 
        '''Test simple ASCII-only data'''

        encoded = self.f.encode_and_sign({'abc': 'def', 'foo': 'bar'})
        expected = set(['abc=def',
                        'foo=bar',
                        'api_sig=57ca69551c24c9c9ce2e2b5c832e61af'
                        ])
        self.assertEqual(expected, set(encoded.split('&')))

        # Order shouldn't matter for the signature
        encoded = self.f.encode_and_sign({'foo': 'bar', 'abc': 'def'})
        self.assertEqual(expected, set(encoded.split('&')))

    def testUnicode(self):
        '''Test Unicode data'''

        # Unicode strings with ASCII data only should result in the
        # same as in the testSimple() test. 
        encoded = self.f.encode_and_sign({'abc': u'def', 'foo': u'bar'})
        expected = set(['abc=def',
                        'foo=bar',
                        'api_sig=57ca69551c24c9c9ce2e2b5c832e61af'
                        ])
        self.assertEqual(expected, set(encoded.split('&')))

        # Non-ASCII UTF-8 data should work too
        # EURO = 0xE2 0x82 0xAC in UTF-8
        # U_UML = 0xC3 0xBC in UTF-8
        data = EURO_UNICODE + U_UML_UNICODE
        encoded = self.f.encode_and_sign({'abc': data.encode('utf-8')})
        expected = set(['abc=%E2%82%AC%C3%BC',
                        'api_sig=51188be8b03d1ee892ade48631bfc0fd'
                        ])
        self.assertEqual(expected, set(encoded.split('&')))

        # Straight Unicode should work too
        data = EURO_UNICODE + U_UML_UNICODE
        encoded = self.f.encode_and_sign({'abc': data})
        self.assertEqual(expected, set(encoded.split('&')))

    def testNoSecret(self):
        
        no_secret = flickrapi.FlickrAPI(key)
        data = EURO_UNICODE + U_UML_UNICODE
        encoded = no_secret.encode_and_sign({'abc': data})
        self.assertEqual('abc=%E2%82%AC%C3%BC', encoded)

class DynamicMethodTest(SuperTest):
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
        super(DynamicMethodTest, self).setUp()

        # Set fake urllib
        self.fake_url_lib = self.FakeUrllib() 
        flickrapi.urllib = self.fake_url_lib
        flickrapi.urllib2 = self.fake_url_lib

    def tearDown(self):
        super(DynamicMethodTest, self).tearDown()

        # Restore original urllib
        flickrapi.urllib = urllib
        flickrapi.urllib2 = urllib2
    
    def test_unicode_args(self):
        '''Tests whether Unicode arguments are properly handled.
        
        Tests using sets, since the order of the URL-encoded arguments
        can't be ensured. The order isn't important anyway.
        '''
        
        # Plain ASCII should work
        self.f.photos_setMeta(monkey='lord')
        sent = set(self.fake_url_lib.data.split('&'))
        expected = set(['api_key=%s' % key, 
                        'monkey=lord', 
                        'method=flickr.photos.setMeta', 
                        'api_sig=edb3c60b63becf1738e2cd8fcc42834a',
                        'format=rest'
                        ])
        self.assertEquals(expected, sent)
         
        # Unicode should work too
        self.f.photos_setMeta(title='monkeylord',
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
        
        self.assertRaises(AttributeError, getattr, self.f, '__get_photos')

    def test_get_dynamic_method(self):
        
        method = self.f.photos_setMeta
        self.assertTrue(hasattr(method, '__call__'))
        self.assertEquals('flickr.photos.setMeta', method.method)

        # Test that we can get it again - should come from the cache,
        # but no way to test that.        
        method = self.f.photos_setMeta
        self.assertTrue(hasattr(method, '__call__'))
        self.assertEquals('flickr.photos.setMeta', method.method)

class WalkerTest(SuperTest):
    '''Tests walk* functions.'''

    def test_walk_set(self):
        # Check that we get a generator
        gen = self.f.walk_set('72157611690250298', per_page=8)
        self.assertEquals(types.GeneratorType, type(gen))

        # I happen to know that that set contains 24 photos, and it is
        # very unlikely that this will ever change (photos of a past
        # event)
        self.assertEquals(24, len(list(gen)))

    def test_walk(self):
        # Check that we get a generator
        gen = self.f.walk(tag_mode='all',
                tags='sybren,365,threesixtyfive,me',
                min_taken_date='2008-08-20',
                max_taken_date='2008-08-30', per_page=8,
                sort='date-taken-desc')
        self.assertEquals(types.GeneratorType, type(gen))

        # very unlikely that this result will ever change
        ids = [p.get('id') for p in gen]
        self.assertEquals(['2824831549', '2807789315', '2807789039',
            '2807773797', '2807772503', '2807771401', '2808616234',
            '2808618120', '2808591736'], ids)

if __name__ == '__main__':
    unittest.main()
