#!/usr/bin/env python

from __future__ import print_function

import time
import requests
from requests.auth import OAuth1
import six
from urlparse import parse_qsl

if six.PY3:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlsplit, parse_qs
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import urlsplit, parse_qs, unquote

url = "http://www.flickr.com/services/oauth/request_token"

class keys:
    apikey = u'a233c66549c9fb5e40a68c1ae156b370'
    apisecret = u'03fbb3ea705fe096'

class OAuthTokenHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # /?oauth_token=72157630789362986-5405f8542b549e95&oauth_verifier=fe4eac402339100e

        qs = urlsplit(self.path).query
        url_vars = parse_qs(qs)

        self.server.oauth_token = url_vars['oauth_token'][0]
        self.server.oauth_verifier = url_vars['oauth_verifier'][0]

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        self.wfile.write('OK')

        #self.server.server_close()
        #self.server.shutdown()

http_server = HTTPServer(('', 8000), OAuthTokenHTTPHandler)

def wait_for_http_request():

    http_server.oauth_verifier = None
    while http_server.oauth_verifier is None:
        http_server.handle_request()

    print('OAuth verifier: %s' % http_server.oauth_verifier)
    return http_server.oauth_verifier



print(120*'=')
print("Part 1: Obtain request token")

params = {
    'oauth_callback': 'oob', #"http://localhost:8000/",
}

import sys
queryoauth = OAuth1(keys.apikey, keys.apisecret, signature_type='query')
r = requests.get(url, params=params, auth=queryoauth,
                 config={'verbose': sys.stderr})

assert isinstance(r, requests.Response)

parts = r.text.split('&')
print('Status code:', r.status_code)
for part in parts:
    print(unquote(part))
print(50 * '-')

############################################################
# Part 2
############################################################

print(120*'=')
print("Part 2: Authorize the request token")

authorize_url = "http://www.flickr.com/services/oauth/authorize"

#parse the content
request_token = dict(parse_qsl(r.text))

print("Request Token:")
print("    - oauth_token        = %s" % request_token['oauth_token'])
print("    - oauth_token_secret = %s" % request_token['oauth_token_secret'])
print()

# Create the token object with returned oauth_token and oauth_token_secret

# You need to authorize this app via your browser.
print("Go to the following link in your browser:")
print("%s?oauth_token=%s&perms=read" % (authorize_url, request_token['oauth_token']))
print()

oauth_verifier = wait_for_http_request()
oauth_verifier = oauth_verifier.decode('ascii')

if http_server.oauth_token != request_token['oauth_token']:
    print("ERROR: received verifier for different OAuth token")
    print("  Expected token: %r" % request_token['oauth_token'])
    print("  Received token: %r" % http_server.oauth_token)

############################################################
# Part 3
############################################################

print(120*'=')
print("Part 3: Exchange request token for an access token")
# url to get access token
access_token_url = "http://www.flickr.com/services/oauth/access_token"

# Now you need to exchange your Request Token for an Access Token

queryoauth = OAuth1(keys.apikey, keys.apisecret,
                    request_token['oauth_token'],
                    request_token['oauth_token_secret'],
                    signature_type='query', verifier=oauth_verifier)
r = requests.get(access_token_url,
                 auth=queryoauth,
                 config={'verbose': sys.stderr})


#parse the response
access_token_resp = {k: v.decode('utf-8') for (k, v) in parse_qsl(r.content)}

#write out a file with the oauth_token and oauth_token_secret
with open('token', 'w') as f:
    for key, value in access_token_resp.items():
        keyvalue = key.encode('utf-8') + '=' + value.encode('utf-8') + '\n'
        f.write(keyvalue)
        sys.stdout.write(keyvalue)
        
        
