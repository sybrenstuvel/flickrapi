#!/usr/bin/env python

'''Unittest for the FlickrAPI.

Far from complete, but it's a start.
'''

import logging
import pkg_resources
import sys
import types
import unittest
import urllib

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

key = u'ecd01ab8f00faf13e1f8801586e126fd'
secret = u'2ee3f558fd79f292'

logging.basicConfig()
LOG = logging.getLogger(__name__)



try:
    from lxml import etree as ElementTree
    LOG.info('REST Parser: using lxml.etree')
except ImportError:
    try:
        import xml.etree.cElementTree as ElementTree
        LOG.info('REST Parser: using xml.etree.cElementTree')
    except ImportError:
        try:
            import xml.etree.ElementTree as ElementTree
            LOG.info('REST Parser: using xml.etree.ElementTree')
        except ImportError:
            try:
                import elementtree.cElementTree as ElementTree
                LOG.info('REST Parser: elementtree.cElementTree')
            except ImportError:
                try:
                    import elementtree.ElementTree as ElementTree
                except ImportError:
                    raise ImportError("You need to install "
                        "ElementTree to use the etree format")


class SuperTest(unittest.TestCase):
    '''Superclass for unittests, provides useful methods.'''
    
    def setUp(self):
        super(SuperTest, self).setUp()

        # Reference to the class under test. Makes it easier to switch to one
        # of the contributed subclasses and run the entire suite.
        #self.clasz = flickrapi.contrib.PersistentFlickrAPI
        self.clasz = flickrapi.FlickrAPI

        self.f = self.clasz(key, secret)
        self.f_noauth = self.clasz(key, secret)

        # Remove/prevent any unwanted tokens
        del self.f.token_cache.token

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

    def test_defaults(self):
        '''Tests _supply_defaults.'''
        
        data = self.f._supply_defaults({'foo': 'bar', 'baz': None, 'token': None},
                                       {'baz': 'foobar', 'room': 'door'})
        self.assertEqual({'foo': 'bar', 'room': 'door'}, data)


    def test_unauthenticated(self):
        '''Test we can access public photos without any authentication/authorization.'''
        
        # make sure this test is made without a valid token in the cache        
        del self.f.token_cache.token

        self.f.photos.getInfo(photo_id='7955646798')

    def test_simple_search(self):
        '''Test simple Flickr search'''
        
        # We expect to be able to find kittens
        result = self.f.photos.search(tags='kitten')
        total = int(result.find('photos').attrib['total'])
        self.assertTrue(total > 0)
    
    def test_token_constructor(self):
        '''Test passing a token to the constructor'''
        
        token = flickrapi.auth.FlickrAccessToken(u'123-abc-def', u'token_secret', u'read',
                                                 u'fullname', u'username', u'user_nsid')
        
        # Pass the token
        flickr = self.clasz(key, secret, token=token)
        
        # It should be in the in-memory token cache now
        self.assertEqual(token, flickr.token_cache.token)
        
        # But not in the on-disk token cache
        self.assertNotEqual(token, flickrapi.OAuthTokenCache(key))              

    def test_upload_without_filename(self):
        '''Uploading a file without filename is impossible'''
        
        self.assertRaises(flickrapi.IllegalArgumentException,
                          self.f.upload, '')
        
        self.assertRaises(flickrapi.IllegalArgumentException,
                          self.f.upload, None)

    def test_upload(self):
        photo = pkg_resources.resource_filename(__name__, 'photo.jpg')

        self.f.authenticate_via_browser(perms='delete')
        result = self.f.upload(photo, is_public=0, is_friend=0, is_family=0, content_type=2)

        # Now remove the photo from the stream again
        photo_id = result.find('photoid').text
        self.f.photos.delete(photo_id=photo_id)

    def test_store_token(self):
        '''Tests that store_token=False FlickrAPI uses SimpleTokenCache'''


        flickr = self.clasz(key, secret, store_token=False)
        self.assertTrue(isinstance(flickr.token_cache, flickrapi.SimpleTokenCache),
                        'Token cache should be SimpleTokenCache, not %r' % flickr.token_cache)

    def test_wrap_in_parser(self):
        '''Tests wrap_in_parser'''

        test = {'wrapped': False}

        def to_wrap(format, test_param):
            self.assertEqual('rest', format)
            self.assertEqual('test_value', test_param)
            test['wrapped'] = True

            return '<rst stat="ok"><element photo_id="5" /></rst>'

        rst = self.f._wrap_in_parser(to_wrap, parse_format='xmlnode',
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

        rst = self.f._wrap_in_parser(to_wrap, parse_format='xmlnode',
                test_param='test_value')
        self.assertEqual('5', rst.element[0]['photo_id'])
        self.assertTrue(test['wrapped'],
                        'Expected wrapped function to be called')


class FormatsTest(SuperTest):
    '''Tests the different parsed formats.
    
    We have to test ElementTree in a bit of a strange way in order to support all
    current flavours of (c)ElementTree.
    '''

    def test_default_format(self):
        '''Test that the default format is etree'''

        f = self.clasz(key, secret)
        etree = f.photos.getInfo(photo_id=u'2333478006')
        self.assertEquals(type(etree), type(ElementTree.Element(None)))

    def test_etree_format_happy(self):
        '''Test ETree format'''

        etree = self.f_noauth.photos.getInfo(photo_id=u'2333478006',
                    format='etree')
        self.assertEquals(type(etree), type(ElementTree.Element(None)))

    def test_etree_format_error(self):
        '''Test ETree format in error conditions'''
 
        self.assertRaises(flickrapi.exceptions.FlickrError,
                self.f_noauth.photos_getInfo, format='etree')

    def test_etree_default_format(self):
        '''Test setting the default format to etree'''

        f = self.clasz(key, secret, format='etree')
        etree = f.photos_getInfo(photo_id=u'2333478006')
        self.assertEquals(type(etree), type(ElementTree.Element(None)))

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
        self.f.authenticate_via_browser()
        gen = self.f.walk(tag_mode='all',
                tags='sybren,365,threesixtyfive,me',
                min_taken_date='2008-08-19',
                max_taken_date='2008-08-31', per_page=7,
                sort='date-taken-desc')
        self.assertEquals(types.GeneratorType, type(gen))

        # very unlikely that this result will ever change. Until it did, of course.
        ids = [p.get('id') for p in gen]
        self.assertEquals(['2824913799', '2824831549', '2807789315', '2807789039',
                           '2807773797', '2807772503', '2807771401', '2808616234',
                           '2808591736', '2807741221'], ids)

if __name__ == '__main__':
    unittest.main()
