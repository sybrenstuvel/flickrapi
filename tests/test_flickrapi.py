#!/usr/bin/env python
# -*- encoding: utf-8 -*-

'''Unittest for the FlickrAPI.

Far from complete, but it's a start.
'''

import json
import logging
import pkg_resources
import sys
import types
import unittest
import urllib
import responses
from urllib.parse import quote_plus, parse_qs

import flickrapi
#flickrapi.set_log_level(logging.FATAL)
flickrapi.set_log_level(logging.DEBUG)

from common_responses import *

print("Testing FlickrAPI version %s" % flickrapi.__version__)

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


class MockedTest(SuperTest):
    """Flickr test in which all HTTP requests are mocked."""

    def setUp(self):
        super(MockedTest, self).setUp()
        self.mock = responses.RequestsMock(assert_all_requests_are_fired=True)
        self.mock.start()

    def tearDown(self):
        self.mock.stop()
        self.mock.reset()
        super(MockedTest, self).tearDown()

    def expect(self, params=None, body='', status=200, content_type='text/xml', method='POST',
               match_querystring=True, urlbase=None):
        """Mocks an expected HTTP query with Responses."""

        if urlbase is None:
            urlbase = self.f.REST_URL

        param_test_callback = None
        url = urlbase

        if params:
            params.setdefault('format', 'rest')
            params.setdefault('nojsoncallback', '1')

        if method == 'GET':
            # The parameters should be on the URL.
            qp = quote_plus
            qs = '&'.join('%s=%s' % (qp(key), qp(str(value).encode('utf-8')))
                          for key, value in sorted(params.items()))
            if qs:
                url = '%s?%s' % (urlbase, qs)

            self.mock.add(method=method, url=url,
                          body=body, status=status,
                          content_type=content_type,
                          match_querystring=match_querystring)
        else:
            # The parameters should be in the request body, not on the URL.
            if params is not None:
                expect_params = {key.encode('utf8'): [value.encode('utf8')]
                                 for key, value in params.items()}

            def param_test_callback(request):
                # This callback can only handle x-www-form-urlencoded requests.
                self.assertEqual('application/x-www-form-urlencoded',
                                 request.headers['Content-Type'].decode('utf8'))
                actual_params = parse_qs(request.body)
                if params is None:
                    self.assertFalse(actual_params)
                else:
                    self.assertEqual(actual_params, expect_params)

                headers = {'Content-Type': 'text/xml'}
                return (status, headers, body)

            self.mock.add_callback(method=method, url=url,
                                   callback=param_test_callback,
                                   content_type=content_type,
                                   match_querystring=match_querystring)

    def expect_auth(self, perms):
        self.mock.add(
            method='POST',
            url=self.f.flickr_oauth.REQUEST_TOKEN_URL,
            body=b'oauth_callback_confirmed=true&'
                 b'oauth_token=cafef00d089843641-e04b4114a40fe037&'
                 b'oauth_token_secret=cafef00dc551b5d7',
            status=200,
            content_type='text/plain;charset=UTF-8',
            match_querystring=False)

        self.mock.add(
            method='POST',
            url=self.f.flickr_oauth.ACCESS_TOKEN_URL,
            body=u'fullname=एकाइ परीक्षकs&&'
                 u'oauth_token=cafef00d089843641-e04b4114a40fe037&'
                 u'oauth_token_secret=cafef00dc551b5d7&'
                 u'username=unittester&'
                 u'user_nsid=1234'.encode('utf-8'),
            status=200,
            content_type='text/plain;charset=UTF-8',
            match_querystring=False)


class FlickrApiTest(MockedTest):
    def test_repr(self):
        '''Class name and API key should be in repr output'''

        r = repr(self.f)
        self.assertIn('FlickrAPI', r)
        self.assertIn(key, r)

    def test_defaults(self):
        '''Tests _supply_defaults.'''

        data = self.f._supply_defaults({'foo': 'bar', 'baz': None, 'token': None},
                                       {'baz': 'foobar', 'room': 'door'})
        self.assertEqual({'foo': 'bar', 'room': 'door'}, data)

    def test_unauthenticated(self):
        '''Test we can access public photos without any authentication/authorization.'''

        # make sure this test is made without a valid token in the cache
        del self.f.token_cache.token

        self.expect({'method': 'flickr.photos.getInfo', 'photo_id': '7955646798'},
                    PHOTO_XML)

        self.f.photos.getInfo(photo_id='7955646798')

    def test_simple_search(self):
        '''Test simple Flickr search'''

        self.expect({'method': 'flickr.photos.search', 'tags': 'kitten'},
                    KITTEN_SEARCH_XML)

        # We expect to be able to find kittens
        result = self.f.photos.search(tags='kitten')
        total = int(result.find('photos').attrib['total'])
        self.assertGreater(total, 0)

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

        from requests_toolbelt.multipart.encoder import MultipartEncoder

        def upload_test_callback(request):
            ct = request.headers['Content-Type']
            self.assertTrue(ct.startswith('multipart/form-data; boundary='))
            self.assertIsInstance(request.body, MultipartEncoder)

            self.assertEqual(request.body.fields['is_public'], b'0')
            self.assertEqual(request.body.fields['is_friend'], b'0')
            self.assertEqual(request.body.fields['is_family'], b'0')
            self.assertEqual(request.body.fields['content_type'], b'2')
            self.assertEqual(request.body.fields['title'], b'photo.jpg')
            self.assertEqual(request.body.fields['api_key'], key.encode('utf8'))
            self.assertIn('photo', request.body.fields)

            headers = {'Content-Type': 'text/xml'}
            return (200, headers, UPLOAD_XML)

        self.expect_auth(perms='delete')
        self.mock.add_callback(method='POST',
                               url=self.f.UPLOAD_URL,
                               callback=upload_test_callback)

        self.f.authenticate_for_test(perms='delete')
        self.f.upload(photo, is_public=0, is_friend=0, is_family=0, content_type=2)

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
        # Photo from Flickr Commons: https://flickr.com/photos/nlireland/45882156715/
        etree = f.photos.getInfo(photo_id=u'45882156715')
        self.assertEqual(type(etree), type(ElementTree.Element(None)))

    def test_etree_format_happy(self):
        '''Test ETree format'''

        etree = self.f_noauth.photos.getInfo(photo_id=u'45882156715',
                    format='etree')
        self.assertEqual(type(etree), type(ElementTree.Element(None)))

    def test_etree_format_error(self):
        '''Test ETree format in error conditions'''

        self.assertRaises(flickrapi.exceptions.FlickrError,
                self.f_noauth.photos_getInfo, format='etree')

    def test_etree_default_format(self):
        '''Test setting the default format to etree'''

        f = self.clasz(key, secret, format='etree')
        etree = f.photos_getInfo(photo_id=u'45882156715')
        self.assertEqual(type(etree), type(ElementTree.Element(None)))

    def test_xmlnode_format(self):
        '''Test XMLNode format'''

        node = self.f_noauth.photos_getInfo(photo_id=u'45882156715',
                    format='xmlnode')
        self.assertNotEqual(None, node.photo[0])

    def test_xmlnode_format_error(self):
        '''Test XMLNode format in error conditions'''

        self.assertRaises(flickrapi.exceptions.FlickrError,
                self.f_noauth.photos_getInfo, format='xmlnode')

    def test_explicit_format(self):
        '''Test explicitly requesting a certain unparsed format'''

        xml = self.f.photos_search(tags='kitten', format='rest')
        self.assertTrue(isinstance(xml, bytes),
                        'XML is type %r, not %r' % (type(xml), bytes))

        # Try to parse it
        rst = flickrapi.XMLNode.parse(xml, False)
        self.assertGreater(int(rst.photos[0]['total']), 0)

    def test_json_format(self):
        '''Test json format (no callback)'''

        data = self.f_noauth.photos.getInfo(photo_id='45882156715',
                                            format='json')
        photo = json.loads(data.decode('utf-8'))
        location = photo['photo']['location']
        if 'locality' not in location:
            raise KeyError('locality not in %r' % location)
        locality = location['locality']

        self.assertEqual(photo['photo']['id'], '45882156715')
        self.assertEqual(locality['_content'], 'Criccieth Castle')

    def test_parsed_json_format(self):
        '''Test parsed json format'''

        photo = self.f_noauth.photos.getInfo(photo_id='45882156715',
                                             format='parsed-json')

        location = photo['photo']['location']
        if 'locality' not in location:
            raise KeyError('locality not in %r' % location)
        locality = location['locality']

        self.assertEqual(photo['photo']['id'], '45882156715')
        self.assertEqual(locality['_content'], 'Criccieth Castle')

    def test_json_callback_format(self):
        '''Test json format (with callback)'''

        data = self.f_noauth.photos.getInfo(photo_id='45882156715',
                                            format='json',
                                            jsoncallback='foobar')
        decoded = data.decode('utf-8')
        self.assertEqual('foobar({', decoded[:8])


class RealWalkerTest(SuperTest):
    """Test walk* functions, on the real, live Flickr API."""

    def test_walk_set(self):
        # Check that we get a generator, and not a list of results.
        gen = self.f.walk_set('72157691267691054', per_page=8)
        self.assertEqual(types.GeneratorType, type(gen))

        # I happen to know that that set contains 10 photos, and it is
        # very unlikely that this will ever change (photos of a past
        # event)
        # https://www.flickr.com/photos/library_of_congress/albums/72157691267691054
        self.assertEqual(10, len(list(gen)))


class MockedWalkerTest(MockedTest):
    """Tests walk* functions on a mocked API for data stability."""

    def test_walk(self):
        # We expect the API to be called more than once, given that there are more results
        # than the per_page parameter allows to fetch in one request.
        self.expect({'method': 'flickr.photos.search', 'per_page': '4', 'page': '1'}, WALK_PAGE_1_XML)
        self.expect({'method': 'flickr.photos.search', 'per_page': '4', 'page': '2'}, WALK_PAGE_2_XML)
        self.expect({'method': 'flickr.photos.search', 'per_page': '4', 'page': '3'}, WALK_PAGE_3_XML)

        # Check that we get a generator, and not a list of results.
        gen = self.f.walk(per_page=4)
        self.assertEqual(types.GeneratorType, type(gen))

        ids = [p.get('id') for p in gen]
        self.assertEqual(['11192308693',
                          '11853287542',
                          '11627471650',
                          '11161255944',
                          '21627488910',
                          '21884772401',
                          '21161270134',
                          '21964432216',
                          '32001923265',
                          '31964437076',
                          '32001922675'], ids)


class TokenCachePathTest(MockedTest):
    def test_token_cache_path(self):
        """Test that the FlickrAPI actually uses the token cache location."""

        import tempfile
        import shutil
        import os.path

        tmpdir = tempfile.mkdtemp()
        try:
            self.f = flickrapi.FlickrAPI(key, secret, token_cache_location=tmpdir)

            # We have to authenticate so that a token is actually written.
            self.expect_auth(perms=u'read')
            self.f.authenticate_for_test(perms=u'read')

            # Check the token cache exists on disk.
            cache_path = os.path.join(tmpdir, 'oauth-tokens.sqlite')
            self.assertTrue(os.path.exists(cache_path))

            # Check the token is stored correctly.
            self.assertEqual('cafef00d089843641-e04b4114a40fe037',
                             self.f.token_cache.token.token)
        finally:
            shutil.rmtree(tmpdir)


if __name__ == '__main__':
    unittest.main()
