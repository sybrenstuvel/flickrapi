#!/usr/bin/env python

from xml.etree import ElementTree as ET
import logging
logging.basicConfig(level=logging.INFO)

from flickrapi import FlickrAPI

class keys:
    apikey = u'a233c66549c9fb5e40a68c1ae156b370'
    apisecret = u'03fbb3ea705fe096'

print('Creating FlickrAPI object')

flickr = FlickrAPI(keys.apikey, keys.apisecret)
#
#token = flickr.token_cache.token
#flickr.flickr_oauth.token = token
#print('Step 0: check token %r' % token.token)
#
#resp = flickr.auth.oauth.checkToken(format='etree')
#ET.dump(resp)
#raise SystemExit()

# ------------------------------------------------------------------------------
print('Step 1: authenticate')
flickr.authenticate_via_browser(perms='read')

# ------------------------------------------------------------------------------
print('Step 2: user Flickr')
resp = flickr.photos.getInfo(photo_id='7658567128')

ET.dump(resp)