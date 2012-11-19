#!/usr/bin/env python

from xml.etree import ElementTree as ET
import logging
import webbrowser
logging.basicConfig(level=logging.INFO)

from flickrapi import FlickrAPI

class keys:
    apikey = u'a233c66549c9fb5e40a68c1ae156b370'
    apisecret = u'03fbb3ea705fe096'

print('Creating FlickrAPI object')

flickr = FlickrAPI(keys.apikey, keys.apisecret)

# ------------------------------------------------------------------------------
print('Step 1: authenticate')

if not flickr.token_valid(perms='read'):
    # Get a request token
    flickr.get_request_token(oauth_callback='oob')
    
    # Open a browser at the authentication URL. Do this however
    # you want, as long as the user visits that URL.
    authorize_url = flickr.auth_url(perms='read')
    webbrowser.open_new_tab(authorize_url)
    
    # Get the verifier code from the user. Do this however you
    # want, as long as the user gives the application the code.
    verifier = unicode(raw_input('Verifier code: '))
    
    # Trade the request token for an access token
    flickr.get_access_token(verifier)

# ------------------------------------------------------------------------------
print('Step 2: use Flickr')
resp = flickr.photos.getInfo(photo_id='7658567128')

ET.dump(resp)
