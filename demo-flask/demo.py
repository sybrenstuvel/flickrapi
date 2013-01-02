#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.INFO)

import flickrapi
from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)

api_key = u'ecd01ab8f00faf13e1f8801586e126fd'
api_secret = u'2ee3f558fd79f292'


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    flickr = flickrapi.FlickrAPI(api_key, api_secret)

    if flickr.token_valid(perms='read'):
        # Already logged in
        print('Already logged in, redirecting to index.')
        return redirect(url_for('index'))

    # Get the request token
    callback = url_for('auth_ok', _external=True)
    print('Getting request token with callback URL %s' % callback)
    flickr.get_request_token(oauth_callback=callback)

    authorize_url = flickr.auth_url(perms='read')

    # Store it in the session, to use in auth_ok()
    session['request_token'] = flickr.flickr_oauth.resource_owner_key
    session['request_token_secret'] = flickr.flickr_oauth.resource_owner_secret
    session['requested_permissions'] = flickr.flickr_oauth.requested_permissions
    print(session)

    print('Redirecting to %s.' % authorize_url)
    return redirect(authorize_url)

@app.route('/auth_ok')
def auth_ok():
    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    flickr.flickr_oauth.resource_owner_key = session['request_token']
    flickr.flickr_oauth.resource_owner_secret = session['request_token_secret']
    flickr.flickr_oauth.requested_permissions = session['requested_permissions']
    verifier = request.args['oauth_verifier']

    print('Getting resource key')
    flickr.get_access_token(verifier)
    return 'Verifier is %s' % verifier

if __name__ == "__main__":
    app.debug = True
    app.secret_key = 'je moeder'
    app.run()

