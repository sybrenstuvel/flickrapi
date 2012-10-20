'''OAuth support functionality
'''

import BaseHTTPServer
import logging
import random
import urlparse
import time
import oauth2 as oauth
import httplib2
import os.path
import sys
import webbrowser

from flickrapi import sockutil, exceptions

class OAuthTokenHTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        # /?oauth_token=72157630789362986-5405f8542b549e95&oauth_verifier=fe4eac402339100e

        qs = urlparse.urlsplit(self.path).query
        url_vars = urlparse.parse_qs(qs)

        self.server.oauth_token = url_vars['oauth_token'][0]
        self.server.oauth_verifier = url_vars['oauth_verifier'][0]

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        self.wfile.write('OK')

class OAuthTokenHTTPServer(BaseHTTPServer.HTTPServer):
    '''HTTP server on a random port, which will receive the OAuth verifier.'''
    
    def __init__(self):
        
        self.log = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))
        
        self.local_addr = self.listen_port()
        self.log.info('Creating HTTP server at %s', self.local_addr)
       
        BaseHTTPServer.HTTPServer.__init__(self, self.local_addr, OAuthTokenHTTPHandler)

        self.oauth_verifier = None
    
    def listen_port(self):
        '''Returns the hostname and TCP/IP port number to listen on.
        
        By default finds a random free port between 1100 and 20000.
        '''

        # Find a random free port
        local_addr = ('localhost', int(random.uniform(1100, 20000)))
        self.log.debug('Finding free port starting at %s', local_addr)
        return sockutil.find_free_port(local_addr)
        
        return local_addr
    
    def wait_for_oauth_verifier(self):
        '''Starts the HTTP server, waits for the OAuth verifier.'''
            
        while self.oauth_verifier is None:
            self.handle_request()
    
        self.log.info('OAuth verifier: %s' % self.oauth_verifier)
        return self.oauth_verifier

    @property
    def oauth_callback_url(self):
        return 'http://localhost:%i/' % self.local_addr[1]

class FlickrAccessToken(oauth.Token):
    '''Flickr access token.
    
    Next to the regular token's key and secret, also contains the authenticated
    user's full name, username and NSID.
    '''
    
    def __init__(self, key, secret, fullname, username, user_nsid):
        
        oauth.Token.__init__(self, key, secret)
        
        self.fullname = fullname
        self.username = username
        self.user_nsid = user_nsid
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return u'FlickrAccessToken(key=%s, fullname=%s, username=%s, user_nsid=%s)' % (
                   self.key, self.fullname, self.username, self.user_nsid) 

    def __repr__(self):
        return str(self)


class OAuthFlickrInterface():
    '''Interface object for handling OAuth-authenticated calls to Flickr.'''

    REQUEST_TOKEN_URL = "http://www.flickr.com/services/oauth/request_token"
    AUTHORIZE_URL = "http://www.flickr.com/services/oauth/authorize"
    ACCESS_TOKEN_URL = "http://www.flickr.com/services/oauth/access_token"

    
    def __init__(self, api_key, api_secret, cache_dir=None):
        self.log = logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

        # Setup the Consumer with the api_keys given by the provider
        self.consumer = oauth.Consumer(key=api_key, secret=api_secret)
        
        self.cache_dir = cache_dir
        self.oauth_token = None

    @property
    def key(self):
        '''Returns the OAuth key'''
        return self.consumer.key

    def _find_cache_dir(self):
        '''Returns the appropriate directory for the HTTP cache.'''
        
        if sys.platform.startswith('win'):
            return os.path.expandvars('%APPDATA%/flickrapi/cache')

    def _create_and_sign_request(self, url, params):
        '''Creates an oauth.Request object.'''
        
        # Create our request. Change method, etc. accordingly.
        req = oauth.Request(method="GET", url=url, parameters=params)
        
        # Create the signature
        signature = oauth.SignatureMethod_HMAC_SHA1().sign(req, self.consumer, self.oauth_token)
        
        # Add the Signature to the request
        req['oauth_signature'] = signature

        return req
    
    def do_request(self, url, params):
        '''Performs the HTTP request, signed with OAuth.
        
        @return: the response content
        '''

        # Default OAuth fluff
        default_params = {
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': str(int(time.time())),
            'oauth_signature_method':"HMAC-SHA1",
            'oauth_version': "1.0",
            'oauth_consumer_key': self.consumer.key,
        }
        
        # If we have an access token, use it!
        if self.oauth_token:
            default_params['oauth_token'] = self.oauth_token.key
        
        default_params.update(params)
        
        req = self._create_and_sign_request(url, default_params)
        
        self.log.debug('Requesting URL %s', req.to_url())
        
        # Make the request to get the oauth_token and the oauth_token_secret
        # I had to directly use the httplib2 here, instead of the oauth library.
        h = httplib2.Http(self.cache_dir)
        headers, content = h.request(req.to_url(), "GET")
        
        # TODO: check the response headers / status code.
        status = headers['status']
        if status != '200':
            self.log.error('do_request: Status code %s received, content:', status)

            for part in content.split('&'):
                self.log.error('    %s', urlparse.unquote(part))
           
            raise exceptions.FlickrError('do_request: Status code %s received' % status)
        
        return content

    def get_request_token(self, oauth_callback):
        '''Requests a new request token.
        
        @param oauth_callback: the URL the user is sent to after granting the token access.
        @return: an oauth.Token object containing the authentication token.
        '''
        
        params = {
            'oauth_callback': oauth_callback,
        }
        
        token_data = self.do_request(self.REQUEST_TOKEN_URL, params)
        self.log.debug('Token data: %s', token_data)
        
        #parse the token data
        request_token = dict(urlparse.parse_qsl(token_data))
        
        # Create the token object with returned oauth_token and oauth_token_secret
        token = oauth.Token(request_token['oauth_token'], 
                            request_token['oauth_token_secret'])

        return token

    def auth_url(self, request_token, perms='read'):
        '''Returns the URL the user should visit to authenticate the given oauth Token.
        
        Use this method in webapps, where you can redirect the user to the returned URL.
        In stand-alone apps, use open_browser_for_authentication instead.
        '''
        
        assert isinstance(request_token, oauth.Token)
        if perms not in {'read', 'write', 'delete'}:
            raise ValueError('Invalid parameter perms=%r' % perms)
        
        return "%s?oauth_token=%s&perms=read" % (self.AUTHORIZE_URL, request_token.key)

#    def open_browser_for_authentication(self, request_token, perms='read'):
#        '''Opens the webbrowser to authenticate the given request request_token, sets the verifier.
#        
#        Use this method in stand-alone apps. In webapps, use auth_url(...) instead,
#        and redirect the user to the returned URL.
#        
#        Updates the given request_token by setting the OAuth verifier.
#        '''
#        
#        url = self.auth_url(request_token, perms)
#        
#        auth_http_server = OAuthTokenHTTPServer()
#                
#        if not webbrowser.open_new_tab(url):
#            raise exceptions.FlickrError('Unable to open a browser to visit %s' % url)
#        
#        oauth_verifier = auth_http_server.wait_for_oauth_verifier()
#        
#        request_token.set_verifier(oauth_verifier)

    def get_access_token(self, request_token):
        '''Exchanges the request token for an access token.

        Also stores the access token in 'self' for easy authentication of subsequent calls.
        
        @return: Access token, a FlickrAccessToken object.
        '''
        
        assert isinstance(request_token, oauth.Token)
        
        if not request_token.verifier:
            # TODO: include a way to solve this error in the error message.
            raise exceptions.IllegalArgumentException('Request token has no verifier.')
        
        params = {
            'oauth_verifier' : request_token.verifier,
        }
        
        self.oauth_token = request_token
        content = self.do_request(self.ACCESS_TOKEN_URL, params)
        
        #parse the response
        access_token_resp = dict(urlparse.parse_qsl(content))
        
        self.oauth_token = FlickrAccessToken(access_token_resp['oauth_token'],
                                              access_token_resp['oauth_token_secret'],
                                              access_token_resp['fullname'],
                                              access_token_resp['username'],
                                              access_token_resp['user_nsid'])
        return self.oauth_token

        
