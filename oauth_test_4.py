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
flickr.authenticate_via_browser(perms='delete')

# ------------------------------------------------------------------------------
print('Step 2: Upload photo')
resp = flickr.upload('tests/photo.jpg', is_public=0, is_friend=0, is_family=0)

from xml.etree import ElementTree as ET
ET.dump(resp)
photo_id = resp.findtext('photoid')

# ------------------------------------------------------------------------------
print('Step 3: Replace photo')

flickr.replace('Vanaf NDSM naar Centrum - begin oktober 2011.jpg', photo_id=photo_id)


# ------------------------------------------------------------------------------
print('Step 4: Delete photo')
flickr.photos.delete(photo_id=photo_id)
