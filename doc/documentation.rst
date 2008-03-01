======================================================================
Python FlickrAPI
======================================================================

:Version: 1.0
:Author: Sybren Stüvel

.. contents::
.. sectnum::

Introduction
======================================================================

`Flickr`_ is one of the most popular photo sharing websites. Their
public API makes it very easy to write applications that use Flickr
some way or another. The possibilities are limitless. This document
describes how to use the Flickr API in your Python programs using the
`Python Flickr API interface`_.


Concepts
----------------------------------------------------------------------

To keep things simple, we do not write "he/she" or "(s)he". We know
that men and women can all be fine programmers and end users. Some
people will be addressed as male, others as female.

To be able to easily talk about Flickr, its users, programmers and
applications, here is an explanation of some concepts we use.


you
    The reader of this document. We assume you are a programmer and
    that you are using this Python Flickr API to create an
    application. In this document we shall address you as male.

application
    The Python application you are creating, that has to interface
    with Flickr.

user
    The user of the application, and thus (either directly or
    indirectly via your application) a Flickr user. In this document
    we shall address the user as female.


Calling API functions
======================================================================

You start by creating a FlickrAPI object with your API key. This key
can be obtained at `Flickr Services`_. Once you have that key, the
cool stuff can begin. Calling a Flickr function is very easy. Here
are some examples::

    import flickrapi

    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

    flickr = flickrapi.FlickrAPI(api_key)
    photos = flickr.photos_search(user_id='73509078@N00', per_page='10')
    sets = flickr.photosets_getList(user_id='73509078@N00')

There is a simple naming scheme here. If the flickr function is called
``flickr.photosets.getList`` just call ``photosets_getList`` on your
``flickr`` object. In other words: replace the dots with underscores.

Return values - XMLNodes
----------------------------------------------------------------------

Flickr sends back XML when you call a function. This XML is parsed
into ``XMLNode`` objects. Attributes in the XML are converted to
dictionary keys with unicode values. Subelements are stored in
properties.

Here is a simple example of the result of above ``sets =
flickr.photosets_getList(...)`` call.

Here is an example of an XML reply::

    <rsp stat='ok'>
        <photosets cancreate="1">
            <photoset id="5" primary="2483" secret="abcdef"
                    server="8" photos="4">
                <title>Test</title>
                <description>foo</description>
            </photoset>
            <photoset id="4" primary="1234" secret="832659"
                    server="3" photos="12">
                <title>My Set</title>
                <description>bar</description>
            </photoset>
        </photosets>
    </rsp>

The ``sets`` variable will be structured as such::

    sets['stat'] = 'ok'
    sets.photosets[0]['cancreate'] = u'1'
    sets.photosets[0].photoset = < a list of XMLNode objects >

    sets.photosets[0].photoset[0]['id'] = u'5'
    sets.photosets[0].photoset[0]['primary'] = u'2483'
    sets.photosets[0].photoset[0]['secret'] = u'abcdef'
    sets.photosets[0].photoset[0]['server'] = u'8'
    sets.photosets[0].photoset[0]['photos'] = u'4'
    sets.photosets[0].photoset[0].title[0].text = u'Test'
    sets.photosets[0].photoset[0].description[0].text = u'foo'

    sets.photosets[0].photoset[1]['id'] = u'4'
    sets.photosets[0].photoset[1]['primary'] = u'1234'
    sets.photosets[0].photoset[1]['secret'] = u'832659'
    sets.photosets[0].photoset[1]['server'] = u'3'
    sets.photosets[0].photoset[1]['photos'] = u'12'
    sets.photosets[0].photoset[1].title[0].text = u'My Set'
    sets.photosets[0].photoset[1].description[0].text = u'bar'

Every ``XMLNode`` also has a ``name`` property. The content of this
property is left as an exercise for the reader.

Future versions of the Python Flickr API might remove this ``XMLNode``
class and offer a DOM interface to the returned XML instead.

Erroneous calls
----------------------------------------------------------------------

When something has gone wrong Flickr will return an error code and a
description of the error. In this case, a ``FlickrError`` exception
will be thrown.

The old behaviour of the Python Flickr API was to simply return the
error code in the XML. However, this is deprecated behaviour as we
strive to notice an error condition as soon as possible. Checking the
return value of every call is not Pythonic. For backward compatibility
you can pass ``fail_on_error=False`` to the ``FlickrAPI`` constructor.

Other response formats
----------------------------------------------------------------------

Flickr supports different response formats, such as JSON and XML-RPC.
If you want, you can use such a different response format. Just add a
``format="json"`` option to the Flickr call. The Python Flickr API
won't parse that format for you, though, so you just get the raw
response::

  >>> f.test_echo(boo='baah', format='json')
  'jsonFlickrApi({"format":{"_content":"json"},
    "auth_token":{"_content":"xxxxx"},
    "boo":{"_content":"baah"},
    "api_sig":{"_content":"xxx"},
    "api_key":{"_content":"xxx"},
    "method":{"_content":"flickr.test.echo"},
    "stat":"ok"})'

You will always get the raw response when you pass the ``format``
parameter. This means that you'll get unparsed XML with
``format="rest"``.

Note that by using the ``format`` parameter the FlickrAPI won't parse
the result, hence it won't be able to check whether a method call
succeeded or not.

Authentication
======================================================================

Her photos may be private. Access to her account is private for sure.
A lot of Flickr API calls require the application to be authenticated.
This means that the user has to tell Flickr that the application is
allowed to do whatever it needs to do.

The Flickr document `User Authentication`_ explains the authentication
process; it's good to know what's in there before you go on.

The document states "The auth_token and api_sig parameters should then
be passed along with each request". You do *not* have to do this - the
Python Flickr API takes care of that.

Here is a simple example of Flickr's two-phase authentication::

    import flickrapi

    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    api_secret = 'YYYYYYYYYYYYYYYY'

    flickr = flickrapi.FlickrAPI(api_key, api_secret)

    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))

The ``api_key`` and ``api_secret`` can be obtained from
http://www.flickr.com/services/api/keys/.

The call to ``flickr.get_token_part_one(...)`` does a lot of things.
First, it checks the on-disk token cache. After all, the application
may be authenticated already. 

If the application isn't authenticated, a browser opens the Flickr
page, on which the user can grant the application the appropriate
access. The application has to wait for the user to do this, hence the
``raw_input("Press ENTER after you authorized this program")``. A GUI
application can use a popup for this, or some other way for the user
to indicate she has performed the authentication ritual.

Once this step is done, we can continue to store the token in the
cache and remember it for future API calls. This is what
``flickr.get_token_part_two(...)`` does.

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

Example using Django
----------------------------------------------------------------------

Here is a simple example in Django_::

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
                 settings.FLICKR_API_SECRET, token=token)

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
             settings.FLICKR_API_SECRET)

     frob = request.GET['frob']
     token = f.get_token(frob)
     request.session['token'] = token

     return HttpResponseRedirect('/content')

 @require_flickr_auth
 def content(request):
     return HttpResponse('Welcome, oh authenticated user!')

Every view that calls an authenticated Flickr method should be
decorated with ``@require_flickr_auth``. For more information on
function decorators, see `PEP 318`_.

The ``callback`` view should be called when the user is sent to the
callback URL as defined in your Flickr API key. The key and secret
should be configured in your settings.py, in the properties
``FLICKR_API_KEY`` and ``FLICKR_API_SECRET``.


Uploading or replacing images
======================================================================

Transferring images requires special attention since they have to
send a lot of data. Therefore they also are a bit different than
advertised in the Flickr API documentation.

flickr.upload(...)
----------------------------------------------------------------------

The ``flickr.upload(...)`` method has the following parameters:

``filename``
    The filename of the image. The image data is read from this file.

``title``
    The title of the photo

``description``
    The description of the photo

``tags``
    Space-delimited list of tags. Tags that contain spaces need to be
    quoted. For example::

        tags='''Amsterdam "central station"'''

    Those are two tags, "Amsterdam" and "central station".

``is_public``
    "1" if the photo is public, "0" if it is private. The default is
    public.

``is_family``
    "1" if the private photo is visible for family, "0" if not. The
    default is not.

``is_friend``
    "1" if the private photo is visible for friends, "0" if not. The
    default is not.

``callback``
    This should be a method that receives two parameters, ``progress``
    and ``done``. The callback method will be called every once in a
    while during uploading. Example::

        def func(progress, done):
            if done:
                print "Done uploading"
            else:
                print "At %s%%" % progress

        flickr.upload(filename='test.jpg', callback=func)
    

flickr.replace(...)
----------------------------------------------------------------------

The ``flickr.replace(...)`` method has the following parameters:

``filename``
    The filename of the image.

``photo_id``
    The identifier of the photo that is to be replaced. Do not use
    this when uploading a new photo.

Only the image itself is replaced, not the other data (title, tags,
comments, etc.).

Unicode and UTF-8
======================================================================

Flickr expects every text to be encoded in UTF-8. The Python Flickr
API can help you in a limited way. If you pass a ``unicode`` string,
it will automatically be encoded to UTF-8 before it's sent to Flickr.
This is the preferred way of working, and is also forward-compatible
with the upcoming Python 3.

If you do not use ``unicode`` strings, you're on your own, and you're
expected to perform the UTF-8 encoding yourself.

Here is an example::

    flickr.photos_setMeta(photo_id='12345',
                          title=u'Money',
                          description=u'Around \u20ac30,-')

This sets the photo's title to "Money" and the description to "Around
€30,-".

Requirements and compatibility
======================================================================

The Python Flickr API only uses built-in Python modules. It is
compatible with Python 2.5 and possibly earlier versions. We strive to
be compatible with older versions, but we have no tests for this yet.

Rendering the documentation requires `Docutils`_.

Links
======================================================================

- `Python Flickr API interface`_
- `Flickr`_
- `Flickr API documentation`_

.. _`Flickr Services`: http://www.flickr.com/services/api/keys/apply/
.. _`Flickr API documentation`: http://www.flickr.com/services/api/
.. _`Flickr API`: http://www.flickr.com/services/api
.. _`Flickr`: http://www.flickr.com/
.. _`Python Flickr API interface`: http://flickrapi.sourceforge.net/
.. _`Docutils`: http://docutils.sourceforge.net/
.. _`User Authentication`:
    http://www.flickr.com/services/api/misc.userauth.html
.. _`Web Applications How-To`:
    http://www.flickr.com/services/api/auth.howto.web.html
.. _Django: http://www.djangoproject.com/
.. _`PEP 318`: http://www.python.org/dev/peps/pep-0318/
