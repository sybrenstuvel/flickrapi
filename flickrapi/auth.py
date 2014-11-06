'''OAuth support functionality
'''

from __future__ import unicode_literals
# Try importing the Python 3 packages first, falling back to 2.x packages when it fails.
try:
    from http import server as http_server
except ImportError:
    import BaseHTTPServer as http_server

try:
    from urllib import parse as urllib_parse
except ImportError:
    import urlparse as urllib_parse

import logging
import random
import os.path
import sys
import webbrowser
import six

from requests_toolbelt import MultipartEncoder
import requests
from requests_oauthlib import OAuth1

from . import sockutil, exceptions, html
from .exceptions import FlickrError

class OAuthTokenHTTPHandler(http_server.BaseHTTPRequestHandler):
    def do_GET(self):
        # /?oauth_token=72157630789362986-5405f8542b549e95&oauth_verifier=fe4eac402339100e

        qs = urllib_parse.urlsplit(self.path).query
        url_vars = urllib_parse.parse_qs(qs)

        oauth_token = url_vars['oauth_token'][0]
        oauth_verifier = url_vars['oauth_verifier'][0]

        if six.PY2:
            self.server.oauth_token = oauth_token.decode('utf-8')
            self.server.oauth_verifier = oauth_verifier.decode('utf-8')
        else:
            self.server.oauth_token = oauth_token
            self.server.oauth_verifier = oauth_verifier

        assert(isinstance(self.server.oauth_token, six.string_types))
        assert(isinstance(self.server.oauth_verifier, six.string_types))

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(html.auth_okay_html)

class OAuthTokenHTTPServer(http_server.HTTPServer):
    '''HTTP server on a random port, which will receive the OAuth verifier.'''
    
    def __init__(self):
        
        self.log = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))
        
        self.local_addr = self.listen_port()
        self.log.info('Creating HTTP server at %s', self.local_addr)
       
        http_server.HTTPServer.__init__(self, self.local_addr, OAuthTokenHTTPHandler)

        self.oauth_verifier = None
    
    def listen_port(self):
        '''Returns the hostname and TCP/IP port number to listen on.
        
        By default finds a random free port between 1100 and 20000.
        '''

        # Find a random free port
        local_addr = ('localhost', int(random.uniform(1100, 20000)))
        self.log.debug('Finding free port starting at %s', local_addr)
        # return local_addr
        return sockutil.find_free_port(local_addr)

    def wait_for_oauth_verifier(self, timeout=None):
        '''Starts the HTTP server, waits for the OAuth verifier.'''
            
        if self.oauth_verifier is None:
            self.timeout = timeout
            self.handle_request()
    
        if self.oauth_verifier:
            self.log.info('OAuth verifier: %s' % self.oauth_verifier)

        return self.oauth_verifier

    @property
    def oauth_callback_url(self):
        return 'http://localhost:%i/' % (self.local_addr[1], )

class FlickrAccessToken(object):
    '''Flickr access token.
    
    Contains the token, token secret, and the user's full name, username and NSID.
    '''
    
    levels = ('read', 'write', 'delete')
    
    def __init__(self, token, token_secret, access_level,
                 fullname=u'', username=u'', user_nsid=u''):
        
        assert isinstance(token, six.text_type), 'token should be unicode text'
        assert isinstance(token_secret, six.text_type), 'token_secret should be unicode text'
        assert isinstance(access_level, six.text_type), 'access_level should be unicode text, is %r' % type(access_level)
        assert isinstance(fullname, six.text_type), 'fullname should be unicode text'
        assert isinstance(username, six.text_type), 'username should be unicode text'
        assert isinstance(user_nsid, six.text_type), 'user_nsid should be unicode text'
        
        access_level = access_level.lower()
        assert access_level in self.levels, 'access_level should be one of %r' % (self.levels, )
        
        self.token = token
        self.token_secret = token_secret
        self.access_level = access_level
        self.fullname = fullname
        self.username = username
        self.user_nsid = user_nsid
    
    def __str__(self):
        return six.text_type(self).encode('utf-8')
    
    def __unicode__(self):
        return 'FlickrAccessToken(token=%s, fullname=%s, username=%s, user_nsid=%s)' % (
                   self.token, self.fullname, self.username, self.user_nsid) 

    def __repr__(self):
        return str(self)

    def has_level(self, access_level):
        '''Returns True iff the token's access level implies the given access level.'''
        
        my_idx = self.levels.index(self.access_level)
        q_idx = self.levels.index(access_level)
    
        return q_idx <= my_idx

class OAuthFlickrInterface(object):
    '''Interface object for handling OAuth-authenticated calls to Flickr.'''

    REQUEST_TOKEN_URL = "https://www.flickr.com/services/oauth/request_token"
    AUTHORIZE_URL = "https://www.flickr.com/services/oauth/authorize"
    ACCESS_TOKEN_URL = "https://www.flickr.com/services/oauth/access_token"

    def __init__(self, api_key, api_secret, oauth_token=None):
        self.log = logging.getLogger('%s.%s' % (self.__class__.__module__, self.__class__.__name__))
        
        assert isinstance(api_key, six.text_type), 'api_key must be unicode string'
        assert isinstance(api_secret, six.text_type), 'api_secret must be unicode string'

        token = None
        secret = None
        if oauth_token.token:
            token = oauth_token.token.token
            secret = oauth_token.token.token_secret

        self.oauth = OAuth1(api_key, api_secret, token, secret, signature_type='auth_header')
        self.oauth_token = oauth_token
        self.auth_http_server = None
        self.requested_permissions = None

    @property
    def key(self):
        '''Returns the OAuth key'''
        return self.oauth.client.client_key

    @property
    def resource_owner_key(self):
        '''Returns the OAuth resource owner key'''
        return self.oauth.client.resource_owner_key

    @resource_owner_key.setter
    def resource_owner_key(self, new_key):
        '''Stores the OAuth resource owner key'''
        self.oauth.client.resource_owner_key = new_key

    @property
    def resource_owner_secret(self):
        '''Returns the OAuth resource owner secret'''
        return self.oauth.client.resource_owner_secret

    @resource_owner_secret.setter
    def resource_owner_secret(self, new_secret):
        '''Stores the OAuth resource owner secret'''
        self.oauth.client.resource_owner_secret = new_secret

    @property
    def verifier(self):
        '''Returns the OAuth verifier.'''
        return self.oauth.client.verifier
    
    @verifier.setter
    def verifier(self, new_verifier):
        '''Sets the OAuth verifier'''
        
        assert isinstance(new_verifier, six.text_type), 'verifier must be unicode text type'
        self.oauth.client.verifier = new_verifier

    @property
    def token(self):
        return self.oauth_token
    
    @token.setter
    def token(self, new_token):
        
        if new_token is None:
            self.oauth_token = None
            self.oauth.client.resource_owner_key = None
            self.oauth.client.resource_owner_secret = None
            self.oauth.client.verifier = None
            self.requested_permissions = None
            return

        assert isinstance(new_token, FlickrAccessToken), new_token
        
        self.oauth_token = new_token
        
        self.oauth.client.resource_owner_key = new_token.token
        self.oauth.client.resource_owner_secret = new_token.token_secret
        self.oauth.client.verifier = None
        self.requested_permissions = new_token.access_level

    def _find_cache_dir(self):
        '''Returns the appropriate directory for the HTTP cache.'''
        
        if sys.platform.startswith('win'):
            return os.path.expandvars('%APPDATA%/flickrapi/cache')
        
        return os.path.expanduser('~/.flickrapi/cache')

    def do_request(self, url, params=None):
        '''Performs the HTTP request, signed with OAuth.
        
        @return: the response content
        '''

        req = requests.get(url,
                           params=params,
                           auth=self.oauth,
                           headers={'Connection': 'close'})
        
        # check the response headers / status code.
        if req.status_code != 200:
            self.log.error('do_request: Status code %i received, content:', req.status_code)

            for part in req.content.split('&'):
                self.log.error('    %s', urllib_parse.unquote(part))
           
            raise exceptions.FlickrError('do_request: Status code %s received' % req.status_code)

        return req.content
    
    def do_upload(self, filename, url, params=None, fileobj=None):
        '''Performs a file upload to the given URL with the given parameters, signed with OAuth.
        
        @return: the response content
        '''

        # work-around for Flickr expecting 'photo' to be excluded
        # from the oauth signature:
        #   1. create a dummy request without 'photo'
        #   2. create real request and use auth headers from the dummy one
        dummy_req = requests.Request('POST', url, data=params,
                                     auth=self.oauth,
                                     headers={'Connection': 'close'})

        prepared = dummy_req.prepare()
        headers = prepared.headers
        self.log.debug('do_upload: prepared headers = %s', headers)

        if not fileobj:
            fileobj = open(filename, 'rb')
        params['photo'] = (os.path.basename(filename), fileobj)
        m = MultipartEncoder(fields=params)
        auth = {'Authorization': headers.get('Authorization'),
                'Content-Type' : m.content_type,
                'Connection'   : 'close'}
        self.log.debug('POST %s', auth)
        req = requests.post(url, data=m, headers=auth)

        # check the response headers / status code.
        if req.status_code != 200:
            self.log.error('do_upload: Status code %i received, content:', req.status_code)

            for part in req.content.split('&'):
                self.log.error('    %s', urllib_parse.unquote(part))
           
            raise exceptions.FlickrError('do_upload: Status code %s received' % req.status_code)
        
        return req.content
        
    
    @staticmethod
    def parse_oauth_response(data):
        '''Parses the data string as OAuth response, returning it as a dict.

        The keys and values of the dictionary will be text strings (i.e. not binary strings).
        '''

        if isinstance(data, six.binary_type):
            data = data.decode('utf-8')
        qsl = urllib_parse.parse_qsl(data)

        resp = {}
        for key, value in qsl:
            resp[key] = value
        
        return resp

    def _start_http_server(self):
        '''Starts the HTTP server, if it wasn't started already.'''
        
        if self.auth_http_server is not None: return
        self.auth_http_server = OAuthTokenHTTPServer()

    def _stop_http_server(self):
        '''Stops the HTTP server, if one was started.'''
        
        if self.auth_http_server is None: return
        self.auth_http_server = None

    def get_request_token(self, oauth_callback=None):
        '''Requests a new request token.
        
        Updates this OAuthFlickrInterface object to use the request token on the following
        authentication calls.
        
        @param oauth_callback: the URL the user is sent to after granting the token access.
            If the callback is None, a local web server is started on a random port, and the
            callback will be http://localhost:randomport/
            
            If you do not have a web-app and you also do not want to start a local web server,
            pass oauth_callback='oob' and have your application accept the verifier from the
            user instead. 
        '''
        
        self.log.debug('get_request_token(oauth_callback=%s):', oauth_callback)

        if oauth_callback is None:
            self._start_http_server()
            oauth_callback = self.auth_http_server.oauth_callback_url
        
        params = {
            'oauth_callback': oauth_callback,
        }
        
        token_data = self.do_request(self.REQUEST_TOKEN_URL, params)
        self.log.debug('Token data: %s', token_data)
        
        # Parse the token data
        request_token = self.parse_oauth_response(token_data)
        self.log.debug('Request token: %s', request_token)
        
        self.oauth.client.resource_owner_key = request_token['oauth_token']
        self.oauth.client.resource_owner_secret = request_token['oauth_token_secret']

    def auth_url(self, perms='read'):
        '''Returns the URL the user should visit to authenticate the given oauth Token.
        
        Use this method in webapps, where you can redirect the user to the returned URL.
        After authorization by the user, the browser is redirected to the callback URL,
        which will contain the OAuth verifier. Set the 'verifier' property on this object
        in order to use it.
        
        In stand-alone apps, use open_browser_for_authentication instead.
        '''
        
        if self.oauth.client.resource_owner_key is None:
            raise FlickrError('No resource owner key set, you probably forgot to call get_request_token(...)')

        if perms not in ('read', 'write', 'delete'):
            raise ValueError('Invalid parameter perms=%r' % perms)
        
        self.requested_permissions = perms
        
        return "%s?oauth_token=%s&perms=%s" % (self.AUTHORIZE_URL, self.oauth.client.resource_owner_key, perms)

    def auth_via_browser(self, perms='read'):
        '''Opens the webbrowser to authenticate the given request request_token, sets the verifier.
        
        Use this method in stand-alone apps. In webapps, use auth_url(...) instead,
        and redirect the user to the returned URL.
        
        Updates the given request_token by setting the OAuth verifier.
        '''
        
        # The HTTP server may have been started already, but we're not sure. Just start
        # it if it needs to be started.
        self._start_http_server()
        
        url = self.auth_url(perms)
        if not webbrowser.open_new_tab(url):
            raise exceptions.FlickrError('Unable to open a browser to visit %s' % url)
        
        self.verifier = self.auth_http_server.wait_for_oauth_verifier()

        # We're now done with the HTTP server, so close it down again.
        self._stop_http_server()
        
    def get_access_token(self):
        '''Exchanges the request token for an access token.

        Also stores the access token in 'self' for easy authentication of subsequent calls.
        
        @return: Access token, a FlickrAccessToken object.
        '''
        
        if self.oauth.client.resource_owner_key is None:
            raise FlickrError('No resource owner key set, you probably forgot to call get_request_token(...)')
        if self.oauth.client.verifier is None:
            raise FlickrError('No token verifier set, you probably forgot to set %s.verifier' % self)
        if self.requested_permissions is None:
            raise FlickrError('Requested permissions are unknown.')

        content = self.do_request(self.ACCESS_TOKEN_URL)
        
        #parse the response
        access_token_resp = self.parse_oauth_response(content)
        
        self.oauth_token = FlickrAccessToken(access_token_resp['oauth_token'],
                                             access_token_resp['oauth_token_secret'],
                                             self.requested_permissions,
                                             access_token_resp.get('fullname', ''),
                                             access_token_resp['username'],
                                             access_token_resp['user_nsid'])
        
        
        self.oauth.client.resource_owner_key = access_token_resp['oauth_token']
        self.oauth.client.resource_owner_secret = access_token_resp['oauth_token_secret']
        self.oauth.client.verifier = None
        
        return self.oauth_token

