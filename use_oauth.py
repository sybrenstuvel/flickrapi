#!/usr/bin/env python

import time
import oauth2 as oauth
import httplib2
import urlparse
import BaseHTTPServer

url = 'http://api.flickr.com/services/rest/'

class keys:
    apikey = 'a233c66549c9fb5e40a68c1ae156b370'
    apisecret = '03fbb3ea705fe096'


# Set the base oauth_* parameters along with any other parameters required
# for the API call.
params = {
	'oauth_timestamp': str(int(time.time())),
	'oauth_signature_method':"HMAC-SHA1",
	'oauth_version': "1.0",
    'oauth_callback': "http://zebra:8000/",
	'oauth_nonce': oauth.generate_nonce(),
	'oauth_consumer_key': keys.apikey,
	'oauth_token': '72157630408061838-0a079792e0c66b9f',
    'oauth_token_secret': 'ed568cb0efdbad93',
    'method': 'flickr.photos.getInfo',
    'format': 'json',
    'nojsoncallback': 1,
    'photo_id': '7658567128',
}

# Setup the Consumer with the api_keys given by the provider
consumer = oauth.Consumer(key=keys.apikey, secret=keys.apisecret)

# Create our request. Change method, etc. accordingly.
req = oauth.Request(method="GET", url=url, parameters=params)

# Create the signature
signature = oauth.SignatureMethod_HMAC_SHA1().sign(req,consumer,None)

# Add the Signature to the request
req['oauth_signature'] = signature

# Make the request to get the oauth_token and the oauth_token_secret
# I had to directly use the httplib2 here, instead of the oauth library.
h = httplib2.Http(".cache")
resp, content = h.request(req.to_url(), "GET")

print content
