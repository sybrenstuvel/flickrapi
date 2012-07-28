#!/usr/bin/env python

import time
import oauth2 as oauth
import httplib2
import urlparse
import BaseHTTPServer

url = "http://www.flickr.com/services/oauth/request_token"

class keys:
    apikey = 'a233c66549c9fb5e40a68c1ae156b370'
    apisecret = '03fbb3ea705fe096'

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

        #self.server.server_close()
        #self.server.shutdown()

http_server = BaseHTTPServer.HTTPServer(('', 8000), OAuthTokenHTTPHandler)

def wait_for_http_request():

    http_server.oauth_verifier = None
    while http_server.oauth_verifier is None:
        http_server.handle_request()

    print 'OAuth verifier: %s' % http_server.oauth_verifier
    return http_server.oauth_verifier

# Set the base oauth_* parameters along with any other parameters required
# for the API call.
params = {
	'oauth_timestamp': str(int(time.time())),
	'oauth_signature_method':"HMAC-SHA1",
	'oauth_version': "1.0",
    'oauth_callback': "http://localhost:8000/",
	'oauth_nonce': oauth.generate_nonce(),
	'oauth_consumer_key': keys.apikey
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
h = httplib2.Http()
resp, content = h.request(req.to_url(), "GET")

print content

############################################################
# Part 2
############################################################

authorize_url = "http://www.flickr.com/services/oauth/authorize"

#parse the content
request_token = dict(urlparse.parse_qsl(content))

print "Request Token:"
print "    - oauth_token        = %s" % request_token['oauth_token']
print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
print

# Create the token object with returned oauth_token and oauth_token_secret
token = oauth.Token(request_token['oauth_token'], 
                    request_token['oauth_token_secret'])

# You need to authorize this app via your browser.
print "Go to the following link in your browser:"
print "%s?oauth_token=%s&perms=read" % (authorize_url, request_token['oauth_token'])
print

oauth_verifier = wait_for_http_request()

if http_server.oauth_token != request_token['oauth_token']:
    print "ERROR: received verifier for different OAuth token"
    print "  Expected token: %r" % request_token['oauth_token']
    print "  Received token: %r" % http_server.oauth_token


# Once you get the verified pin, input it
#accepted = 'n'
#while accepted.lower() != 'y':
#    accepted = raw_input('Have you authorized me? (y/n) ')
#oauth_verifier = raw_input('What is the oauth_verifier? ')

#set the oauth_verifier token
token.set_verifier(oauth_verifier)


############################################################
# Part 3
############################################################


# url to get access token
access_token_url = "http://www.flickr.com/services/oauth/access_token"

# Now you need to exchange your Request Token for an Access Token
# Set the base oauth_* parameters along with any other parameters required
# for the API call.
access_token_parms = {
    'oauth_consumer_key': keys.apikey,
    'oauth_nonce': oauth.generate_nonce(),
    'oauth_signature_method':"HMAC-SHA1",
    'oauth_timestamp': str(int(time.time())),
    'oauth_token':request_token['oauth_token'],
    'oauth_verifier' : oauth_verifier
}

#setup request
req = oauth.Request(method="GET", url=access_token_url, 
                    parameters=access_token_parms)

#create the signature
signature = oauth.SignatureMethod_HMAC_SHA1().sign(req,consumer,token)

# assign the signature to the request
req['oauth_signature'] = signature

#make the request
h = httplib2.Http()
resp, content = h.request(req.to_url(), "GET")

#parse the response
access_token_resp = dict(urlparse.parse_qsl(content))
print access_token_resp

#write out a file with the oauth_token and oauth_token_secret
with open('token', 'w') as f:
    f.write(access_token_resp['oauth_token'] + '\n')
    f.write(access_token_resp['oauth_token_secret'] + '\n')

