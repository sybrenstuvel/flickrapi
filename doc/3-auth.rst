
Authentication and Authorization
======================================================================

For authentication and authorization Flickr uses
`OAuth 1.0a <http://oauth.net/core/1.0a/>`_. This ensures that in one
flow, the user is authenticated via the Flickr website, and the application
is authorized by the user to act in its name.

The user's photos may be private. Access to her account is private for sure.
A lot of Flickr API calls require the application to be authorized.
This means that the user has to tell Flickr that the application is
allowed to do whatever it needs to do.

The Flickr document `User Authentication`_ explains the authentication
process; it's good to know what's in there before you go on. The Python
Flickr API takes care of most of the OAuth details, but still it is
important to know the authentication flow.

Here is a simple example::

    import flickrapi

    api_key = u'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    api_secret = u'YYYYYYYYYYYYYYYY'

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    flickr.authenticate_via_browser(perms='read')

The ``api_key`` and ``api_secret`` can be obtained from
http://www.flickr.com/services/api/keys/.

The call to ``flickr.authenticate_via_browser(...)`` does a lot of things.
First, it checks the on-disk token cache. After all, the application
may be authenticated already. If a token is found, it is checked with
Flickr for validity. If it is valid, it is used for all
following calls and the authentication process is complete.

If the application isn't authenticated yet, a browser opens the Flickr
page, on which the user can grant the application the appropriate
access. When the user presses the "OK, I'LL AUTHORIZE IT" button, the
browser will be redirected to a local web server to pass a
verification code to the application. When this code has been received,
the token is stored in the token cache and the authentication process is complete.

.. _`User Authentication`: http://www.flickr.com/services/api/auth.oauth.html

Authenticating without local web server
----------------------------------------------------------------------

By default a webbrowser is started to let the user perform the
authentication. A local web server is then started to receive the OAuth
verifier code. Upon authorizing the application the browser is sent to this
web server, where ``FlickrAPI`` obtains the verifier code.

However, this may not be appropriate or even possible in your application.
When a local web server is not used, you can use "out of band" passing of
the verifier code::

    import flickrapi
    import webbrowser

    api_key = u'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    api_secret = u'YYYYYYYYYYYYYYYY'

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    
    print('Step 1: authenticate')
    
    # Only do this if we don't have a valid token already
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
  
    print('Step 2: use Flickr')
    resp = flickr.photos.getInfo(photo_id='7658567128')


Authenticating web applications
----------------------------------------------------------------------

When working with web applications, things are a bit different. The
user using the application (through a browser) is likely to be
different from the user running the server-side software.

We'll assume you're following Flickr's `Web Applications How-To`_, and
just tell you how things are splified when working with the Python
Flickr API.

    3. Create a login link. Use ``flickr.web_login_url(perms)``` for
       that.  It'll return the login link for you, given the
       permissions you passed in the ``perms`` parameter.

    5. Don't bother understanding the signing process; the
       ``FlickrAPI`` module takes care of that for you. Once you
       received the frob from Flickr, use
       ``flickr.get_token("the_frob")``. The FlickrAPI module will
       remember the token for you.

    6. You can safely skip this, and just use the FlickrAPI module as
       usual. Only read this if you want to understand how the
       FlickrAPI module signs method calls for you.

Token handling in web applications
----------------------------------------------------------------------

Web applications have two kinds of users: identified and anonymous
users. If your users are identified, you can pass their name (or other
means of identification) as the ``username`` parameter to the
``FlickrAPI`` constructor, and get a FlickrAPI instance that's bound
to that user. It will keep track of the authentication token for that
user, and there's nothing special you'll have to do.

When working with anonymous users, you'll have to store the
authentication token in a cookie. In step 5. above, use this::

    token = flickr.get_token("the_frob")

Then use your web framework to store the token in a cookie. When
reading a token from a cookie, pass it on to the FlickrAPI constructor
like this::

    flickr = flickrapi.FlickrAPI(api_key, api_secret, token=token)

It won't be stored in the on-disk token cache - which is a good thing,
since

    A. you don't know who the user is, so you wouldn't be able to
       retrieve the appropriate tokens for visiting users.

    B. the tokens are stored in cookies, so there is no need to store
       them in another place.

Preventing usage of on-disk token cache
----------------------------------------------------------------------

Another way of preventing the storage of tokens is to pass
``store_token=False`` as the constructor parameter. Use this if you
want to be absolutely sure that the FlickrAPI instance doesn't use any
previously stored tokens, nor that it will store new tokens.

Controlling the location of the on-disk token cache
----------------------------------------------------------------------

By default the authentication tokens are stored in the directory
``~/.flickr``. If you want to change this directory, you can do so
by changing the ``flickr.token.path`` variable after you have created
the ``FlickrAPI`` instance::

    import flickrapi

    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    api_secret = 'YYYYYYYYYYYYYYYY'

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    flickr.token.path = '/tmp/flickrtokens'

    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))
 
Multiple processes using the same key
----------------------------------------------------------------------

By default the token is stored on the filesystem in
``somepath/<authentication key>/auth.token``. When multiple
processes use the same authentication key a race condition can occur
where the authentication token is removed. To circumvent this, use the
``LockingTokenCache`` instead::

    from flickrapi import FlickrAPI
    from flickrapi.tokencache import LockingTokenCache
    
    flickr = flickrapi.FlickrAPI(api_key, secret)
    
    flickr.token_cache = LockingTokenCache(api_key)
    # -- or --
    flickr.token_cache = LockingTokenCache(api_key, username)

This cache ensures that only one process at the time can use the token
cache. It does not forsee in multi-threading.

As the locking mechanism causes additional disk I/O and performs more
checks, it is slower than the regular cache. Since not that many
people use the same key in parallel on one machine (or a shared
filesystem on which the token is stored) the default token cache does
not use locking.

Example using Django
----------------------------------------------------------------------

Here is a simple example in `Django <https://www.djangoproject.com/>`_::

 import flickrapi
 from django.conf import settings
 from django.http import HttpResponseRedirect, HttpResponse

 import logging
 logging.basicConfig()

 log = logging.getLogger(__name__)
 log.setLevel(logging.DEBUG)

 def require_flickr_auth(view):
     '''View decorator, redirects users to Flickr when no valid
     authentication token is available.
     '''

     def protected_view(request, *args, **kwargs):
         if 'token' in request.session:
             token = request.session['token']
             log.info('Getting token from session: %s' % token)
         else:
             token = None
             log.info('No token in session')

        f = flickrapi.FlickrAPI(settings.FLICKR_API_KEY,
                settings.FLICKR_API_SECRET, token=token,
                store_token=False)

         if token:
             # We have a token, but it might not be valid
             log.info('Verifying token')
             try:
                 f.auth_checkToken() 
             except flickrapi.FlickrError:
                 token = None 
                 del request.session['token']

         if not token:
             # No valid token, so redirect to Flickr
             log.info('Redirecting user to Flickr to get frob')
             url = f.web_login_url(perms='read')
             return HttpResponseRedirect(url)

         # If the token is valid, we can call the decorated view.
         log.info('Token is valid')
         
         return view(request, *args, **kwargs)

     return protected_view

 def callback(request):
     log.info('We got a callback from Flickr, store the token')

    f = flickrapi.FlickrAPI(settings.FLICKR_API_KEY,
            settings.FLICKR_API_SECRET, store_token=False)

     frob = request.GET['frob']
     token = f.get_token(frob)
     request.session['token'] = token

     return HttpResponseRedirect('/content')

 @require_flickr_auth
 def content(request):
     return HttpResponse('Welcome, oh authenticated user!')

Every view that calls an authenticated Flickr method should be
decorated with ``@require_flickr_auth``. For more information on
function decorators, see `PEP 318 <http://www.python.org/dev/peps/pep-0318/>`_.

The ``callback`` view should be called when the user is sent to the
callback URL as defined in your Flickr API key. The key and secret
should be configured in your settings.py, in the properties
``FLICKR_API_KEY`` and ``FLICKR_API_SECRET``.
