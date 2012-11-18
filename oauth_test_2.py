#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.DEBUG)

from flickrapi import auth

class keys:
    apikey = u'a233c66549c9fb5e40a68c1ae156b370'
    apisecret = u'03fbb3ea705fe096'

print('Creating OAuth interface')
flickr_oauth = auth.OAuthFlickrInterface(keys.apikey, keys.apisecret)

# ------------------------------------------------------------------------------
print('Step 1: obtain a request token')
flickr_oauth.get_request_token()

# ------------------------------------------------------------------------------
print('Step 2: let the user authenticate the token')
flickr_oauth.auth_via_browser('read')

# ------------------------------------------------------------------------------
print('Step 3: exchange for an access token')
flickr_oauth.get_access_token()

# ------------------------------------------------------------------------------
print('Step 4: use Flickr!')

params = {
    'method': 'flickr.photos.getInfo',
    'format': 'json',
    'nojsoncallback': 1,
    'photo_id': '7658567128',
}
print(flickr_oauth.do_request('http://api.flickr.com/services/rest/', params))
