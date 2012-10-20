#!/usr/bin/env python

import logging
import webbrowser

logging.basicConfig(level=logging.DEBUG)

from flickrapi import auth, exceptions

class keys:
    apikey = 'a233c66549c9fb5e40a68c1ae156b370'
    apisecret = '03fbb3ea705fe096'

print('Creating HTTP server object')
auth_http_server = auth.OAuthTokenHTTPServer()

print('Creating OAuth interface')
flickr_oauth = auth.OAuthFlickrInterface(keys.apikey, keys.apisecret)

# ------------------------------------------------------------------------------
print('Step 1: obtain a request token')

oauth_callback = auth_http_server.oauth_callback_url
request_token = flickr_oauth.get_request_token(oauth_callback)

# ------------------------------------------------------------------------------
print('Step 2: let the user authenticate the token')

url = flickr_oauth.auth_url(request_token, perms='read')
if not webbrowser.open_new_tab(url):
    raise exceptions.FlickrError('Unable to open a browser to visit %s' % url)

oauth_verifier = auth_http_server.wait_for_oauth_verifier()
request_token.set_verifier(oauth_verifier)

# ------------------------------------------------------------------------------
print('Step 3: exchange for an access token')

flickr_oauth.get_access_token(request_token)

# ------------------------------------------------------------------------------
print('Step 4: use Flickr!')

params = {
    'method': 'flickr.photos.getInfo',
    'format': 'json',
    'nojsoncallback': 1,
    'photo_id': '7658567128',
}
print(flickr_oauth.do_request('http://api.flickr.com/services/rest/', params))
