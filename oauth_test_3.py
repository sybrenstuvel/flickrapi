#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.INFO)

from flickrapi import FlickrAPI

class keys:
    apikey = u'a233c66549c9fb5e40a68c1ae156b370'
    apisecret = u'03fbb3ea705fe096'

print('Creating FlickrAPI object')

flickr = FlickrAPI(keys.apikey, keys.apisecret)

# ------------------------------------------------------------------------------
print('Step 1: authenticate')
flickr.authenticate_via_browser(perms='read')

# ------------------------------------------------------------------------------
print('Step 2: user Flickr')
resp = flickr.photos.getInfo(photo_id='7658567128')

from xml.etree import ElementTree as ET
ET.dump(resp)